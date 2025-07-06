from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton
import bcrypt
from controllers.data import basic_style


class UpdatePasswordDialog(QDialog):
    def __init__(self, user, parent=None):
        super().__init__(parent)
        self.setStyleSheet(basic_style)
        layout = QVBoxLayout(self)
        self.old_user_password = user[2]
        self.setWindowTitle(f"Upravit heslo {user[1]}")


        self.old_password_label = QLabel("Zadej staré heslo:")
        layout.addWidget(self.old_password_label)
        self.old_password = QLineEdit()
        self.old_password.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.old_password)

        self.new_password_label = QLabel("Zadej nové heslo:")
        layout.addWidget(self.new_password_label)
        self.new_password = QLineEdit()
        self.new_password.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.new_password)

        self.confirm_password_label = QLabel("Potvrď nové heslo:")
        layout.addWidget(self.confirm_password_label)
        self.confirm_password = QLineEdit()
        self.confirm_password.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.confirm_password)

        button_layout = QHBoxLayout()
        ok_button = QPushButton("Změnit heslo")
        ok_button.clicked.connect(self.accept)
        ok_button.clicked.disconnect()
        ok_button.clicked.connect(self.try_accept)
        cancel_button = QPushButton("Zrušit")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)

    def check_passwords(self):
        # Kontrola vyplnění polí
        if not self.old_password.text():
            self.old_password.setText("")
            self.new_password.setText("")
            self.confirm_password.setText("")
            self.old_password.setPlaceholderText("Zadej staré heslo")
            self.old_password_label.setText("Zadej staré heslo (povinné pole)")
            self.old_password_label.setStyleSheet("color: red;")
            return False
        if not bcrypt.checkpw(self.old_password.text().encode('utf-8'), self.old_user_password.encode('utf-8')):
            self.old_password.setText("")
            self.new_password.setText("")
            self.confirm_password.setText("")
            self.old_password.setPlaceholderText("Hesla se neshodují")
            self.old_password_label.setText("Staré a nové heslo se neshodují")
            self.old_password_label.setStyleSheet("color: red;")
            return False
        if not self.new_password.text():
            self.old_password.setText("")
            self.confirm_password.setText("")
            self.new_password.setPlaceholderText("Zadej nové heslo")
            self.new_password_label.setText("Zadej nové heslo (povinné pole)")
            self.new_password_label.setStyleSheet("color: red;")
            return False
        if not self.confirm_password.text():
            self.old_password.setText("")
            self.new_password.setText("")
            self.confirm_password.setPlaceholderText("Potvrď nové heslo")
            self.confirm_password_label.setText("Potvrď nové heslo (povinné pole)")
            self.confirm_password_label.setStyleSheet("color: red;")
            return False
        if self.old_password.text() == self.new_password.text():
            self.old_password.setText("")
            self.new_password.setText("")
            self.confirm_password.setText("")
            self.old_password.setPlaceholderText("Nové heslo nesmí být stejné jako staré")
            self.old_password_label.setText("Nové heslo nesmí být stejné jako staré")
            self.new_password_label.setText("Nové heslo nesmí být stejné jako staré")
            self.new_password_label.setStyleSheet("color: red;")
            self.confirm_password_label.setText("Nové heslo nesmí být stejné jako staré")
            self.confirm_password_label.setStyleSheet("color: red;")
            return False
        if self.new_password.text() != self.confirm_password.text():
            self.old_password.setText("")
            self.new_password.setText("")
            self.confirm_password.setText("")
            self.confirm_password.setPlaceholderText("Nová hesla se neshodují")
            self.confirm_password_label.setText("Nová hesla se neshodují")
            self.confirm_password_label.setStyleSheet("color: red;")
            return False
        return True

    def get_data(self):
        if not self.check_passwords():
            return None
        return {
            "new_password":  self.password_crypt(self.new_password.text())
        }

    def try_accept(self):
      if self.check_passwords():
        self.accept()
        
    @staticmethod
    def password_crypt(password):
        """Zahashuje heslo pomocí bcrypt."""
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode()
        

from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QComboBox
from models.users import get_user_by_name
from controllers.data import basic_style
import bcrypt

class AddUserDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Přidat uživatele")
        self.setModal(True)
        self.setStyleSheet(basic_style)
        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("Jméno uživatele:"))
        self.username_edit = QLineEdit()
        layout.addWidget(self.username_edit)

        layout.addWidget(QLabel("Heslo:"))
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password_edit)
        
        layout.addWidget(QLabel("Heslo znovu:"))
        self.password_again = QLineEdit()
        self.password_again.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password_again)

        layout.addWidget(QLabel("Role:"))
        self.role_combo = QComboBox()
        self.role_combo.addItems(["user", "supervisor"])
        layout.addWidget(self.role_combo)

        button_layout = QHBoxLayout()
        self.ok_button = QPushButton("Přidat")
        self.ok_button.clicked.connect(self.accept)
        self.ok_button.clicked.disconnect()
        self.ok_button.clicked.connect(self.try_accept)
        self.cancel_button = QPushButton("Zrušit")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)
        layout.addLayout(button_layout)

    def get_data(self):
        if not self.check_empty_fields():
            return None
        hashed_password = bcrypt.hashpw(self.password_edit.text().encode(), bcrypt.gensalt()).decode()
        return {
            "username": self.username_edit.text(),
            "password": hashed_password,
            "role": self.role_combo.currentText()
        }
        
    def check_empty_fields(self):
        if not self.username_edit.text():
            self.username_edit.setPlaceholderText("Zadej jméno uživatele")
            self.username_edit.setStyleSheet("color: red;")
            return False
        if not self.password_edit.text():
            self.password_edit.setText("")
            self.password_edit.setPlaceholderText("Zadej heslo")
            self.password_edit.setStyleSheet("color: red;")
            return False
        if not self.password_again.text():
            self.password_again.setText("")
            self.password_again.setPlaceholderText("Zadej heslo znovu")
            self.password_again.setStyleSheet("color: red;")
            return False
        if self.password_edit.text() != self.password_again.text():
            self.password_again.setText("")
            self.password_edit.setText("")
            self.password_again.setPlaceholderText("Hesla se neshodují.")
            self.password_edit.setPlaceholderText("Hesla se neshodují.")
            self.password_again.setStyleSheet("color: red;")
            return False
        if get_user_by_name(self.username_edit.text()):
            self.username_edit.setText("")
            self.username_edit.setPlaceholderText("Uživatel již existuje")
            self.username_edit.setStyleSheet("color: red;")
            return False
        return True
      
    def try_accept(self):
      if self.check_empty_fields():
          self.accept()
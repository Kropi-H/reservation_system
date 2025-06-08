from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QComboBox
import bcrypt

class AddUserDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Přidat uživatele")
        self.setModal(True)
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
        self.cancel_button = QPushButton("Zrušit")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)
        layout.addLayout(button_layout)

    def get_data(self):
        if not self.username_edit.text() or not self.password_edit.text() or not self.password_again.text():
            raise ValueError("Všechna pole musí být vyplněna.")
        if self.password_edit.text() != self.password_again.text():
            raise ValueError("Hesla se neshodují.")
        hashed_password = bcrypt.hashpw(self.password_edit.text().encode(), bcrypt.gensalt()).decode()
        return {
            "username": self.username_edit.text(),
            "password": hashed_password,
            "role": self.role_combo.currentText()
        }
from PySide6.QtWidgets import QDialog, QFormLayout, QLineEdit, QDialogButtonBox
import bcrypt

from models.databaze import get_user_by_username

class LoginDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Přihlášení")
        layout = QFormLayout(self)
        self.username = QLineEdit()
        self.password = QLineEdit()
        self.password.setEchoMode(QLineEdit.Password)
        layout.addRow("Jméno:", self.username)
        layout.addRow("Heslo:", self.password)
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.try_login)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        self.login_success = False
        self.role = ""

    def try_login(self):
        username = self.username.text()
        password = self.password.text()
        user = get_user_by_username(username)
        if user and bcrypt.checkpw(password.encode(), user['password_hash'].encode()):
            self.login_success = True
            self.accept()
            self.role = user['role']
        else:
            self.username.setText("")
            self.password.setText("")
            self.username.setPlaceholderText("Neplatné jméno nebo heslo")
            self.password.setPlaceholderText("Zkuste znovu")

    def get_credentials(self):
        return self.username.text(), self.password.text()
    
    def get_name_and_role(self):
        return self.username.text(), self.role

'''
def hash_password(password):
    """
    Hashes the password using bcrypt.
    """
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
  
print(hash_password("magdamagda"))  # Example usage, remove in production
'''
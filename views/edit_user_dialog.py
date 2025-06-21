from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QComboBox
from models.users import get_user_by_name
class EditUserDialog(QDialog):
    def __init__(self, username, role, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Upravit uživatele")
        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("Jméno uživatele:"))
        self.username_edit = QLineEdit(username)
        layout.addWidget(self.username_edit)

        layout.addWidget(QLabel("Role:"))
        self.role_combo = QComboBox()
        self.role_combo.addItems(["user", "supervisor"])
        self.role_combo.setCurrentText(role)
        layout.addWidget(self.role_combo)

        button_layout = QHBoxLayout()
        ok_button = QPushButton("Uložit")
        ok_button.clicked.connect(self.accept)
        ok_button.clicked.disconnect()
        ok_button.clicked.connect(self.try_accept)
        cancel_button = QPushButton("Zrušit")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)

    def get_data(self):
        if not self.check_empty_fields():
            return None
        return {
            "username": self.username_edit.text(),
            "role": self.role_combo.currentText()
        }
        
    def check_empty_fields(self):
        if not self.username_edit.text():
            self.username_edit.setPlaceholderText("Zadej jméno uživatele")
            self.username_edit.setStyleSheet("color: red;")
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
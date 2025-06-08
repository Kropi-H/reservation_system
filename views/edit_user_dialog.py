from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QComboBox

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
        cancel_button = QPushButton("Zrušit")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)

    def get_data(self):
        return {
            "username": self.username_edit.text(),
            "role": self.role_combo.currentText()
        }
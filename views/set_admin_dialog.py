from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog, QVBoxLayout, QPushButton, QLabel, QLineEdit
from controllers.data import basic_style

class SetAdminDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Nastavení administrátora - Veterinární rezervační systém")
        self.setModal(True)
        self.setFixedSize(400, 200)
        # Inicializace dialogu pro nastavení administrátora
        self.init_ui()
        self.setStyleSheet(basic_style)

    def init_ui(self):
        layout = QVBoxLayout()

        # Popis
        description_label = QLabel("Zadejte údaje pro nového administrátora:")
        layout.addWidget(description_label)
        
        name_label = QLabel("Jméno:")
        layout.addWidget(name_label)
        self.name = QLineEdit()
        self.name.setPlaceholderText("Zadejte jméno administrátora")
        layout.addWidget(self.name)
        
        password_label = QLabel("Heslo:")
        layout.addWidget(password_label)
        self.password = QLineEdit()
        self.password.setEchoMode(QLineEdit.Password)
        self.password.setPlaceholderText("Zadejte heslo administrátora")
        layout.addWidget(self.password)
        
        repeat_password_label = QLabel("Zopakujte heslo:")
        layout.addWidget(repeat_password_label)
        self.repeat_password = QLineEdit()
        self.repeat_password.setEchoMode(QLineEdit.Password)
        self.repeat_password.setPlaceholderText("Zopakujte heslo administrátora")
        layout.addWidget(self.repeat_password)

        # Tlačítko pro potvrzení
        confirm_button = QPushButton("Potvrdit")
        confirm_button.clicked.connect(self.accept)
        layout.addWidget(confirm_button)

        self.setLayout(layout)
        
    def valid_data(self):
        """Zkontroluje, zda jsou zadané údaje platné."""
        if not self.name.text():
            self.name.setPlaceholderText("Zadejte jméno")
            return False
        if not self.password.text():
            self.password.setPlaceholderText("Zadejte heslo")
            return False
        if self.password.text() != self.repeat_password.text():
            self.repeat_password.setPlaceholderText("Hesla se neshodují")
            return False
        return True
    
    def return_data(self):
        if not self.valid_data():
            return None
        # Vrátí data z dialogu, pokud jsou platná 
        else:
            return {
                "name": self.name.text(),
                "password": self.password.text()
            }

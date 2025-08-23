from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, 
    QLineEdit, QPushButton, QLabel, QComboBox, QSpinBox,
    QCheckBox, QMessageBox, QGroupBox
)
from PySide6.QtCore import Qt
import json
import os

class ChatConfigDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Nastavení chatu")
        self.setFixedSize(400, 350)
        self.setModal(True)
        
        # Načtení aktuální konfigurace
        self.config_path = os.path.join(os.path.dirname(__file__), "../chat/chat_config.json")
        self.load_config()
        
        self.setup_ui()
        
    def load_config(self):
        """Načte konfiguraci z chat_config.json"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
        except:
            # Výchozí konfigurace
            self.config = {
                "mode": "client",
                "server_ip": "127.0.0.1",
                "server_port": 12345,
                "auto_start_server": False,
                "username": "Uživatel"
            }
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Hlavní formulář
        form_layout = QFormLayout()
        
        # Uživatelské jméno
        self.username_input = QLineEdit(self.config.get("username", "Uživatel"))
        self.username_input.setPlaceholderText("Zadejte své jméno")
        form_layout.addRow("Uživatelské jméno:", self.username_input)
        
        # Režim práce
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["client", "server"])
        current_mode = self.config.get("mode", "client")
        self.mode_combo.setCurrentText(current_mode)
        self.mode_combo.currentTextChanged.connect(self.on_mode_changed)
        form_layout.addRow("Režim:", self.mode_combo)
        
        # IP adresa serveru
        self.server_ip_input = QLineEdit(self.config.get("server_ip", "127.0.0.1"))
        self.server_ip_input.setPlaceholderText("IP adresa serveru")
        form_layout.addRow("IP serveru:", self.server_ip_input)
        
        # Port serveru
        self.server_port_input = QSpinBox()
        self.server_port_input.setRange(1024, 65535)
        self.server_port_input.setValue(self.config.get("server_port", 12345))
        form_layout.addRow("Port serveru:", self.server_port_input)
        
        # Auto start server
        self.auto_start_checkbox = QCheckBox("Automaticky spustit server při režimu 'server'")
        self.auto_start_checkbox.setChecked(self.config.get("auto_start_server", False))
        form_layout.addRow(self.auto_start_checkbox)
        
        layout.addLayout(form_layout)
        
        # Informační sekce
        info_group = QGroupBox("Informace")
        info_layout = QVBoxLayout(info_group)
        
        info_text = QLabel("""
        <b>Režim 'client':</b> Připojí se k existujícímu serveru<br>
        <b>Režim 'server':</b> Spustí vlastní server pro ostatní<br><br>
        <i>Pro místní síť použijte IP 0.0.0.0 v režimu server</i>
        """)
        info_text.setWordWrap(True)
        info_text.setStyleSheet("QLabel { padding: 10px; }")
        info_layout.addWidget(info_text)
        
        layout.addWidget(info_group)
        
        # Tlačítka
        buttons_layout = QHBoxLayout()
        
        self.ok_button = QPushButton("OK")
        self.ok_button.clicked.connect(self.accept_config)
        
        self.cancel_button = QPushButton("Zrušit")
        self.cancel_button.clicked.connect(self.reject)
        
        buttons_layout.addWidget(self.ok_button)
        buttons_layout.addWidget(self.cancel_button)
        
        layout.addLayout(buttons_layout)
        
        # Inicializace stavu podle režimu
        self.on_mode_changed(current_mode)
    
    def on_mode_changed(self, mode):
        """Upraví dostupnost polí podle vybraného režimu"""
        if mode == "server":
            self.server_ip_input.setText("0.0.0.0")
            self.server_ip_input.setEnabled(True)
            self.auto_start_checkbox.setEnabled(True)
        else:
            if self.server_ip_input.text() == "0.0.0.0":
                self.server_ip_input.setText("127.0.0.1")
            self.server_ip_input.setEnabled(True)
            self.auto_start_checkbox.setEnabled(False)
            self.auto_start_checkbox.setChecked(False)
    
    def accept_config(self):
        """Uloží konfiguraci a zavře dialog"""
        username = self.username_input.text().strip()
        
        if not username:
            QMessageBox.warning(self, "Chyba", "Uživatelské jméno nesmí být prázdné!")
            return
        
        # Vytvoření nové konfigurace
        new_config = {
            "mode": self.mode_combo.currentText(),
            "server_ip": self.server_ip_input.text().strip(),
            "server_port": self.server_port_input.value(),
            "auto_start_server": self.auto_start_checkbox.isChecked(),
            "username": username
        }
        
        # Uložení do souboru
        try:
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(new_config, f, indent=4, ensure_ascii=False)
            
            self.config = new_config
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, "Chyba", f"Nepodařilo se uložit konfiguraci:\n{str(e)}")
    
    def get_config(self):
        """Vrátí uloženou konfiguraci"""
        return self.config

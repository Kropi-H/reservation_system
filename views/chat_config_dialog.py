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
        
        # Určení cesty ke konfiguračnímu souboru
        self.config_path = self.get_config_path()
        self.load_config()
        
        self.setup_ui()
    
    def get_config_path(self):
        """Získá správnou cestu ke konfiguračnímu souboru podle prostředí a OS"""
        import sys
        import platform
        
        if getattr(sys, 'frozen', False):
            # Produkční executable - použij OS-specifické umístění
            system = platform.system().lower()
            
            if system == 'windows':
                # Windows: AppData\Local
                base_dir = os.environ.get('LOCALAPPDATA', os.path.expanduser('~'))
            elif system == 'darwin':  # macOS
                # macOS: ~/Library/Application Support
                base_dir = os.path.expanduser('~/Library/Application Support')
            else:  # Linux a další Unix-like systémy
                # Linux: ~/.config (XDG_CONFIG_HOME)
                base_dir = os.environ.get('XDG_CONFIG_HOME', os.path.expanduser('~/.config'))
            
            app_dir = os.path.join(base_dir, "ReservationSystem")
            
            # Vytvoř složku, pokud neexistuje
            os.makedirs(app_dir, exist_ok=True)
            
            config_path = os.path.join(app_dir, "chat_config.json")
            print(f"ChatConfigDialog: PROD {platform.system()} - config v: {config_path}")
            
            # Backward kompatibilita - přesuň config z vedle executable
            old_config = os.path.join(os.path.dirname(sys.executable), "chat_config.json")
            if os.path.exists(old_config) and not os.path.exists(config_path):
                try:
                    import shutil
                    shutil.move(old_config, config_path)
                    print(f"ChatConfigDialog: Přesunut config z {old_config} do {config_path}")
                except Exception as e:
                    print(f"ChatConfigDialog: Chyba při přesunu: {e}")
        else:
            # Vývojové prostředí - původní lokace
            script_dir = os.path.dirname(os.path.abspath(__file__))
            config_path = os.path.join(script_dir, "../chat/chat_config.json")
            print(f"ChatConfigDialog: DEV režim - config v: {config_path}")
        
        return config_path
        
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
        
        self.reset_button = QPushButton("Resetovat chat")
        self.reset_button.clicked.connect(self.reset_chat)
        self.reset_button.setStyleSheet("""
            QPushButton {
                background-color: #ff9800;
                color: white;
                font-weight: bold;
                padding: 8px 16px;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #f57c00;
            }
        """)
        
        self.ok_button = QPushButton("OK")
        self.ok_button.clicked.connect(self.accept_config)
        
        self.cancel_button = QPushButton("Zrušit")
        self.cancel_button.clicked.connect(self.reject)
        
        buttons_layout.addWidget(self.reset_button)
        buttons_layout.addStretch()
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
            self.auto_start_checkbox.setChecked(True)  # Automaticky zapni pro server režim
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
    
    def reset_chat(self):
        """Resetuje aktuální chat"""
        reply = QMessageBox.question(
            self, 
            "Resetovat chat",
            "Opravdu chcete resetovat chat? Tím se zavře stávající připojení a vymaže se historie zpráv.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Získej referenci na hlavní okno
            main_window = self.parent()
            if main_window and hasattr(main_window, 'reset_chat'):
                main_window.reset_chat()
                QMessageBox.information(self, "Chat resetován", "Chat byl úspěšně resetován.")
            else:
                QMessageBox.warning(self, "Chyba", "Nepodařilo se najít hlavní okno pro reset chatu.")
    
    def get_config(self):
        """Vrátí uloženou konfiguraci"""
        return self.config

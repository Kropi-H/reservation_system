import os
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton, 
                               QLabel, QLineEdit, QSpinBox, QMessageBox, QTextEdit,
                               QCheckBox, QGroupBox, QFormLayout, QProgressBar)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont, QPixmap
from config import (save_database_config, test_database_connection, 
                    get_network_database_configs, save_network_database_config,
                    set_active_network_config)
from controllers.data import basic_style
import psycopg2

class PostgreSQLSetupDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Nastavení PostgreSQL databáze - Veterinární rezervační systém")
        self.setStyleSheet(basic_style)
        self.setModal(True)
        self.setFixedSize(600, 500)
        self.connection_successful = False
        self.setup_ui()
        self.load_saved_configs()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Nadpis
        title_label = QLabel("Konfigurace PostgreSQL databáze")
        title_font = QFont()
        title_font.setBold(True)
        title_font.setPointSize(14)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # Popis
        description_label = QLabel(
            "Aplikace vyžaduje připojení k PostgreSQL databázi.\n"
            "Zadejte parametry připojení nebo vyberte uloženou konfiguraci."
        )
        description_label.setAlignment(Qt.AlignCenter)
        description_label.setWordWrap(True)
        layout.addWidget(description_label)
        
        # Hlavní obsahová oblast
        content_layout = QHBoxLayout()
        
        # Levá strana - konfigurace
        config_group = QGroupBox("Parametry připojení")
        config_layout = QFormLayout()
        
        # Server
        self.host_input = QLineEdit()
        self.host_input.setPlaceholderText("localhost nebo IP adresa")
        self.host_input.setText("192.168.0.118")
        config_layout.addRow("Server:", self.host_input)
        
        # Port
        self.port_input = QSpinBox()
        self.port_input.setRange(1, 65535)
        self.port_input.setValue(5432)
        config_layout.addRow("Port:", self.port_input)
        
        # Databáze
        self.database_input = QLineEdit()
        self.database_input.setPlaceholderText("název databáze")
        self.database_input.setText("veterina")
        config_layout.addRow("Databáze:", self.database_input)
        
        # Uživatel
        self.user_input = QLineEdit()
        self.user_input.setPlaceholderText("uživatelské jméno")
        self.user_input.setText("postgres")
        config_layout.addRow("Uživatel:", self.user_input)
        
        # Heslo
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setPlaceholderText("heslo")
        config_layout.addRow("Heslo:", self.password_input)
        
        # Zobrazit heslo
        self.show_password = QCheckBox("Zobrazit heslo")
        self.show_password.stateChanged.connect(self.toggle_password_visibility)
        config_layout.addRow("", self.show_password)
        
        config_group.setLayout(config_layout)
        content_layout.addWidget(config_group)
        
        # Pravá strana - uložené konfigurace
        saved_group = QGroupBox("Uložené konfigurace")
        saved_layout = QVBoxLayout()
        
        self.saved_configs_label = QLabel("Žádné uložené konfigurace")
        saved_layout.addWidget(self.saved_configs_label)
        
        # Tlačítka pro uložené konfigurace
        self.config_buttons_layout = QVBoxLayout()
        saved_layout.addLayout(self.config_buttons_layout)
        
        saved_group.setLayout(saved_layout)
        content_layout.addWidget(saved_group)
        
        layout.addLayout(content_layout)
        
        # Status oblast
        status_group = QGroupBox("Status připojení")
        status_layout = QVBoxLayout()
        
        self.status_text = QTextEdit()
        self.status_text.setMaximumHeight(80)
        self.status_text.setReadOnly(True)
        self.status_text.setPlainText("Připraveno k testování připojení...")
        status_layout.addWidget(self.status_text)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        status_layout.addWidget(self.progress_bar)
        
        status_group.setLayout(status_layout)
        layout.addWidget(status_group)
        
        # Tlačítka
        buttons_layout = QHBoxLayout()
        
        self.test_button = QPushButton("Test připojení")
        self.test_button.clicked.connect(self.test_connection)
        buttons_layout.addWidget(self.test_button)
        
        self.save_button = QPushButton("Uložit konfiguraci")
        self.save_button.clicked.connect(self.save_configuration)
        buttons_layout.addWidget(self.save_button)
        
        self.connect_button = QPushButton("Připojit a pokračovat")
        self.connect_button.clicked.connect(self.connect_and_continue)
        self.connect_button.setEnabled(False)
        buttons_layout.addWidget(self.connect_button)
        
        self.exit_button = QPushButton("Ukončit aplikaci")
        self.exit_button.clicked.connect(self.reject)
        buttons_layout.addWidget(self.exit_button)
        
        layout.addLayout(buttons_layout)
        self.setLayout(layout)
        
        # Connect input changes to update status
        for input_widget in [self.host_input, self.database_input, self.user_input, self.password_input]:
            input_widget.textChanged.connect(self.reset_connection_status)
        self.port_input.valueChanged.connect(self.reset_connection_status)
    
    def toggle_password_visibility(self):
        """Přepíná viditelnost hesla."""
        if self.show_password.isChecked():
            self.password_input.setEchoMode(QLineEdit.Normal)
        else:
            self.password_input.setEchoMode(QLineEdit.Password)
    
    def reset_connection_status(self):
        """Resetuje status připojení při změně parametrů."""
        self.connection_successful = False
        self.connect_button.setEnabled(False)
        self.status_text.setPlainText("Parametry byly změněny. Otestujte připojení znovu.")
    
    def get_config(self):
        """Vrátí konfiguraci z formuláře."""
        return {
            'host': self.host_input.text().strip(),
            'port': self.port_input.value(),
            'database': self.database_input.text().strip(),
            'user': self.user_input.text().strip(),
            'password': self.password_input.text()
        }
    
    def set_config(self, config):
        """Nastaví konfiguraci do formuláře."""
        self.host_input.setText(config.get('host', ''))
        self.port_input.setValue(config.get('port', 5432))
        self.database_input.setText(config.get('database', ''))
        self.user_input.setText(config.get('user', ''))
        self.password_input.setText(config.get('password', ''))
    
    def load_saved_configs(self):
        """Načte uložené konfigurace."""
        configs = get_network_database_configs()
        
        # Vyčistí staré tlačítka
        for i in reversed(range(self.config_buttons_layout.count())):
            child = self.config_buttons_layout.itemAt(i).widget()
            if child:
                child.setParent(None)
        
        if configs:
            self.saved_configs_label.setText(f"Nalezeno {len(configs)} konfigurací:")
            
            for name, config in configs.items():
                button = QPushButton(f"{name} ({config['host']}:{config['port']})")
                button.clicked.connect(lambda checked, cfg=config, n=name: self.load_config(cfg, n))
                self.config_buttons_layout.addWidget(button)
        else:
            self.saved_configs_label.setText("Žádné uložené konfigurace")
    
    def load_config(self, config, name):
        """Načte konkrétní konfiguraci."""
        self.set_config(config)
        self.status_text.setPlainText(f"Načtena konfigurace '{name}'. Otestujte připojení.")
        self.reset_connection_status()
    
    def test_connection(self):
        """Testuje připojení k databázi."""
        config = self.get_config()
        
        # Validace
        if not all([config['host'], config['database'], config['user']]):
            self.status_text.setPlainText("❌ Vyplňte prosím všechna povinná pole (server, databáze, uživatel).")
            return
        
        # Zobrazit progress
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate progress
        self.test_button.setEnabled(False)
        self.status_text.setPlainText(f"🔍 Testování připojení k {config['host']}:{config['port']}...")
        
        # Test s timeoutem
        try:
            conn = psycopg2.connect(
                host=config['host'],
                port=config['port'],
                database=config['database'],
                user=config['user'],
                password=config['password'],
                connect_timeout=5
            )
            
            # Test základního dotazu
            cursor = conn.cursor()
            cursor.execute("SELECT version()")
            version = cursor.fetchone()[0]
            cursor.close()
            conn.close()
            
            self.status_text.setPlainText(
                f"✅ Připojení úspěšné!\n"
                f"Server: {config['host']}:{config['port']}\n"
                f"Verze: {version[:60]}..."
            )
            
            self.connection_successful = True
            self.connect_button.setEnabled(True)
            
        except psycopg2.OperationalError as e:
            error_msg = str(e)
            
            if "could not connect to server" in error_msg:
                self.status_text.setPlainText(
                    f"❌ Nelze se připojit k serveru {config['host']}:{config['port']}\n\n"
                    "Zkontrolujte:\n"
                    "• Je PostgreSQL server spuštěn?\n"
                    "• Je server dostupný ze sítě?\n"
                    "• Je povolený port ve firewall?\n"
                    "• Je listen_addresses = '*' v postgresql.conf?"
                )
            elif "authentication failed" in error_msg:
                self.status_text.setPlainText(
                    f"❌ Autentifikace selhala\n\n"
                    "Zkontrolujte:\n"
                    "• Uživatelské jméno a heslo\n"
                    "• Konfigurace pg_hba.conf\n"
                    "• Oprávnění uživatele"
                )
            elif "database" in error_msg and "does not exist" in error_msg:
                self.status_text.setPlainText(
                    f"❌ Databáze '{config['database']}' neexistuje\n\n"
                    "Vytvořte databázi pomocí:\n"
                    f"CREATE DATABASE {config['database']};"
                )
            else:
                self.status_text.setPlainText(f"❌ Chyba připojení:\n{error_msg}")
            
            self.connection_successful = False
            self.connect_button.setEnabled(False)
            
        except Exception as e:
            self.status_text.setPlainText(f"❌ Neočekávaná chyba:\n{str(e)}")
            self.connection_successful = False
            self.connect_button.setEnabled(False)
        
        finally:
            self.progress_bar.setVisible(False)
            self.test_button.setEnabled(True)
    
    def save_configuration(self):
        """Uloží konfiguraci."""
        if not self.connection_successful:
            reply = QMessageBox.question(
                self,
                "Neuložená konfigurace",
                "Připojení nebylo úspěšně otestováno. Chcete konfiguraci uložit přesto?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            if reply != QMessageBox.Yes:
                return
        
        # Dialog pro název konfigurace
        from PySide6.QtWidgets import QInputDialog
        name, ok = QInputDialog.getText(
            self,
            "Název konfigurace",
            "Zadejte název pro tuto konfiguraci:",
            text=f"{self.host_input.text()}_server"
        )
        
        if ok and name.strip():
            config = self.get_config()
            save_network_database_config(name.strip(), config)
            self.load_saved_configs()
            QMessageBox.information(self, "Uloženo", f"Konfigurace '{name}' byla uložena.")
        
    def connect_and_continue(self):
        """Připojí se k databázi a pokračuje v aplikaci."""
        if not self.connection_successful:
            QMessageBox.warning(
                self,
                "Chyba",
                "Nejprve úspěšně otestujte připojení k databázi."
            )
            return
        
        config = self.get_config()
        
        # Uložit jako aktivní konfiguraci
        save_database_config(config)
        
        # Také uložit do síťových konfigurací
        save_network_database_config('current_connection', config)
        set_active_network_config('current_connection')
        
        self.status_text.setPlainText("✅ Konfigurace uložena. Spouštění aplikace...")
        
        # Krátké zpoždění pro zobrazení zprávy
        QTimer.singleShot(500, self.accept)
    
    def is_connection_successful(self):
        """Vrátí True pokud bylo připojení úspěšné."""
        return self.connection_successful

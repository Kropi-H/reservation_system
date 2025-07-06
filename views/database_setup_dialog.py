import os
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton, 
                               QLabel, QFileDialog, QMessageBox)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from models.databaze import inicializuj_databazi
from config import get_last_directory
from controllers.data import basic_style
import shutil

class DatabaseSetupDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Nastavení databáze - Veterinární rezervační systém")
        self.setStyleSheet(basic_style)
        self.setModal(True)
        self.setFixedSize(450, 250)
        self.database_path = ""
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Nadpis
        title_label = QLabel("Databáze není nastavena")
        title_font = QFont()
        title_font.setBold(True)
        title_font.setPointSize(12)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # Popis
        description_label = QLabel("Pro pokračování je potřeba nastavit databázi.\nVyberte jednu z následujících možností:")
        description_label.setAlignment(Qt.AlignCenter)
        description_label.setWordWrap(True)
        layout.addWidget(description_label)
        
        # Tlačítka
        buttons_layout = QVBoxLayout()
        
        # Tlačítko pro připojení existující databáze
        connect_button = QPushButton("Připojit existující databázi")
        connect_button.clicked.connect(self.connect_existing_database)
        buttons_layout.addWidget(connect_button)
        
        # Tlačítko pro vytvoření nové databáze
        create_button = QPushButton("Vytvořit novou databázi")
        create_button.clicked.connect(self.create_new_database)
        buttons_layout.addWidget(create_button)
        
        # Tlačítko pro ukončení
        exit_button = QPushButton("Ukončit aplikaci")
        exit_button.clicked.connect(self.reject)
        buttons_layout.addWidget(exit_button)
        
        layout.addLayout(buttons_layout)
        self.setLayout(layout)
        
    def connect_existing_database(self):
        """Otevře dialog pro výběr existující databáze."""
        last_dir = get_last_directory()
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Vyberte databázový soubor",
            last_dir,
            "SQLite databáze (*.db *.sqlite *.sqlite3);;Všechny soubory (*)"
        )
        
        if file_path:
            # Zkontroluj, zda je soubor skutečně SQLite databáze
            if self.is_valid_sqlite_database(file_path):
                self.database_path = file_path
                self.accept()
            else:
                QMessageBox.warning(
                    self,
                    "Neplatná databáze",
                    "Vybraný soubor není platná SQLite databáze."
                )
    
    def create_new_database(self):
        """Otevře dialog pro vytvoření nové databáze."""
        last_dir = get_last_directory()
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Vytvořit novou databázi",
            os.path.join(last_dir, "veterina.db"),
            "SQLite databáze (*.db);;Všechny soubory (*)"
        )
        
        if file_path:
            # Pro nové databáze nemusíme validovat SQLite strukturu
            # pouze zkontrolujeme, že cesta je platná
            try:
                # Zkontroluj, zda je cesta zapisovatelná
                directory = os.path.dirname(file_path)
                if not os.path.exists(directory):
                    os.makedirs(directory, exist_ok=True)
                
                # Ujisti se, že soubor má správnou příponu
                if not file_path.endswith('.db'):
                    file_path += '.db'
                
                # Zkontroluj, zda soubor již neexistuje
                if os.path.exists(file_path):
                    reply = QMessageBox.question(
                        self,
                        "Soubor již existuje",
                        f"Soubor '{file_path}' již existuje. Chcete ho přepsat?",
                        QMessageBox.Yes | QMessageBox.No,
                        QMessageBox.No
                    )
                    if reply != QMessageBox.Yes:
                        return
                
                self.database_path = file_path
                self.accept()
                
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Chyba",
                    f"Nepodařilo se vytvořit databázi: {str(e)}"
                )
    
    def is_valid_sqlite_database(self, file_path):
        """Zkontroluje, zda je soubor platná SQLite databáze."""
        try:
            import sqlite3
            conn = sqlite3.connect(file_path)
            conn.execute("SELECT name FROM sqlite_master WHERE type='table';")
            conn.close()
            return True
        except:
            return False
    
    def get_database_path(self):
        """Vrátí cestu k vybrané databázi."""
        return self.database_path

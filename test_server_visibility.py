#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test server viditelnosti zpráv od klientů
"""

import sys
import os
import json
import time

# Přidání cesty k projektovému adresáři
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PySide6.QtWidgets import QApplication, QVBoxLayout, QWidget, QLabel, QPushButton
from chat.chat_widget import ChatWidget

def create_config(mode, username, server_ip="127.0.0.1", server_port=12345):
    """Vytvoří konfiguraci pro test"""
    config = {
        "mode": mode,
        "server_ip": server_ip,
        "server_port": server_port,
        "auto_start_server": mode == "server",
        "username": username
    }
    
    config_path = os.path.join(os.path.dirname(__file__), "chat", "chat_config.json")
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=4, ensure_ascii=False)
    print(f"Konfigurace vytvořena pro {mode}: {username}")

class TestServerVisibility(QWidget):
    def __init__(self, mode, username):
        super().__init__()
        self.mode = mode
        self.username = username
        self.setWindowTitle(f"Test Server Visibility - {mode} - {username}")
        self.setGeometry(100 if mode == "server" else 600, 100, 500, 700)
        
        layout = QVBoxLayout()
        
        # Info
        info = QLabel(f"Režim: {mode}\nUživatel: {username}")
        layout.addWidget(info)
        
        # Testovací popis
        if mode == "server":
            desc = QLabel("SERVER: Měl by vidět svoje zprávy OKAMŽITĚ\na zprávy od klientů PO PŘIPOJENÍ")
        else:
            desc = QLabel("CLIENT: Měl by vidět svoje zprávy jako ECHO\na zprávy od serveru")
        layout.addWidget(desc)
        
        # Konfigurace
        create_config(mode, username)
        
        # Chat widget
        self.chat = ChatWidget(username)
        layout.addWidget(self.chat)
        
        # Test tlačítko
        test_btn = QPushButton(f"Pošli test zprávu od {username}")
        test_btn.clicked.connect(self.send_test)
        layout.addWidget(test_btn)
        
        self.setLayout(layout)

    def send_test(self):
        if self.chat.message_input:
            self.chat.message_input.setText(f"Test zpráva od {self.username}")
            self.chat.send_message()

def main():
    app = QApplication(sys.argv)
    
    # Nejdříve vytvoříme server
    server_window = TestServerVisibility("server", "Server")
    server_window.show()
    
    # Počkáme na spuštění serveru a jeho připojení
    app.processEvents()
    time.sleep(3)
    
    # Pak vytvoříme klienta
    client_window = TestServerVisibility("client", "Klient")
    client_window.show()
    
    print("=== Test server visibility ===")
    print("1. Server by měl vidět svoje zprávy okamžitě")
    print("2. Server by měl vidět zprávy od klientů po připojení") 
    print("3. Client by měl vidět zprávy jako echo ze serveru")
    print("4. Pošlete zprávy z obou oken a ověřte viditelnost")
    
    app.exec()

if __name__ == "__main__":
    main()

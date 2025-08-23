#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Debug tool pro chat - zobrazuje log zpráv
"""

import sys
import os
import time
import threading

# Přidání cesty k projektovému adresáři
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PySide6.QtWidgets import QApplication, QVBoxLayout, QWidget, QPushButton, QLabel, QTextEdit, QHBoxLayout
from PySide6.QtCore import QTimer, Signal, QObject
from chat.chat_widget import ChatWidget

class ChatDebugWidget(ChatWidget):
    """Rozšířený chat widget s debug informacemi"""
    
    def __init__(self, username, server_host='127.0.0.1', server_port=12345):
        super().__init__(username, server_host, server_port)
        
        # Přidání debug textu
        self.debug_text = QTextEdit()
        self.debug_text.setMaximumHeight(150)
        self.debug_text.setPlaceholderText("Debug log...")
        
        # Vložení debug textu do layoutu
        layout = self.layout()
        layout.insertWidget(1, QLabel("Debug log:"))
        layout.insertWidget(2, self.debug_text)
        
    def show_message(self, msg):
        """Přepsaná metoda s debug logem"""
        super().show_message(msg)
        self.debug_text.append(f"RECEIVED: {msg}")
        
    def send_message(self):
        """Přepsaná metoda s debug logem"""
        msg = self.message_input.text().strip()
        if msg:
            self.debug_text.append(f"SENDING: {self.username}: {msg}")
        super().send_message()

class ChatDebugWindow(QWidget):
    def __init__(self, username, mode="client"):
        super().__init__()
        self.setWindowTitle(f"Chat Debug - {username} ({mode})")
        self.setGeometry(100, 100, 450, 700)
        
        layout = QVBoxLayout()
        
        # Info
        info = QLabel(f"Uživatel: {username}\nRežim: {mode}")
        info.setStyleSheet("font-weight: bold; padding: 5px; background: #f0f0f0;")
        layout.addWidget(info)
        
        # Chat widget
        if mode == "server":
            # Nejprve změníme konfiguraci na server režim
            import json
            config_path = os.path.join("chat", "chat_config.json")
            with open(config_path, 'w') as f:
                json.dump({
                    "mode": "server",
                    "server_ip": "0.0.0.0",
                    "server_port": 12345,
                    "auto_start_server": True,
                    "username": username
                }, f, indent=4)
        
        self.chat = ChatDebugWidget(username, "127.0.0.1", 12345)
        layout.addWidget(self.chat)
        
        self.setLayout(layout)

def main():
    """Spustí debug chat"""
    app = QApplication(sys.argv)
    
    if len(sys.argv) > 1 and sys.argv[1] == "server":
        window = ChatDebugWindow("Server", "server")
    else:
        window = ChatDebugWindow(f"Klient_{int(time.time()) % 1000}", "client")
    
    window.show()
    app.exec()

if __name__ == "__main__":
    main()

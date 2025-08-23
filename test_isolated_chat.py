#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Izolovaný test chat - server a klient
"""

import sys
import os
import threading
import time

# Přidání cesty k projektovému adresáři
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PySide6.QtWidgets import QApplication, QVBoxLayout, QWidget, QLabel, QHBoxLayout
from chat.chat_widget import ChatWidget
from chat.chat_server import ChatServer

class TestChatWidget(ChatWidget):
    """Chat widget bez závislosti na konfiguraci"""
    def load_config(self):
        # Přepíšeme načítání konfigurace
        if hasattr(self, '_test_mode'):
            self.config = self._test_mode
        else:
            self.config = {"mode": "client", "auto_start_server": False}

class TestWindow(QWidget):
    def __init__(self, title, username, mode="client"):
        super().__init__()
        self.setWindowTitle(title)
        self.setGeometry(100, 100, 400, 600)
        
        layout = QVBoxLayout()
        
        # Info
        info = QLabel(f"Režim: {mode}\nUživatel: {username}")
        info.setStyleSheet("font-weight: bold; padding: 10px; background: #f0f0f0;")
        layout.addWidget(info)
        
        # Chat widget
        self.chat = TestChatWidget(username, "127.0.0.1", 12345)
        self.chat._test_mode = {"mode": mode, "auto_start_server": False}
        layout.addWidget(self.chat)
        
        self.setLayout(layout)

def start_server():
    """Spustí server v separátním vlákně"""
    server = ChatServer()
    # Nastavíme parametry serveru přímo
    server.host = "127.0.0.1"
    server.port = 12345
    try:
        print("=== SERVER: Spouštím chat server ===")
        server.start()
    except Exception as e:
        print(f"Server error: {e}")

def test_isolated_chat():
    """Test izolovaného chatu"""
    
    # Spustíme server v separátním vlákně
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()
    
    # Počkáme na spuštění serveru
    time.sleep(2)
    
    # Spustíme GUI
    app = QApplication(sys.argv)
    
    # Server okno
    server_window = TestWindow("Chat Server", "Server", "server")
    server_window.move(50, 50)
    
    # Klient okno
    client_window = TestWindow("Chat Klient", "Klient", "client")
    client_window.move(500, 50)
    
    server_window.show()
    client_window.show()
    
    app.exec()

if __name__ == "__main__":
    test_isolated_chat()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test opravené komunikace mezi serverem a klientem
"""

import sys
import os
import json
import threading
import time

# Přidání cesty k projektovému adresáři
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PySide6.QtWidgets import QApplication
from chat.chat_widget import ChatWidget
from chat.chat_server import ChatServer

def start_test_server():
    """Spustí test server"""
    server = ChatServer()
    server.host = "127.0.0.1"
    server.port = 12345
    print("=== STARTUJU TEST SERVER ===")
    try:
        server.start()
    except Exception as e:
        print(f"Server error: {e}")

def create_test_config(mode, username):
    """Vytvoří test konfiguraci"""
    config_path = os.path.join("chat", "chat_config.json")
    config = {
        "mode": mode,
        "server_ip": "127.0.0.1" if mode == "client" else "0.0.0.0",
        "server_port": 12345,
        "auto_start_server": mode == "server",
        "username": username
    }
    
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=4)
    print(f"Konfigurace vytvořena pro {mode}: {username}")

def test_fixed_chat():
    """Test opravené chat funkcionality"""
    
    # Spusť server v separátním vlákně
    server_thread = threading.Thread(target=start_test_server, daemon=True)
    server_thread.start()
    time.sleep(2)  # Počkej na spuštění serveru
    
    app = QApplication(sys.argv)
    
    # Klient 1 konfigurace
    create_test_config("client", "Klient1")
    client1 = ChatWidget("Klient1", "127.0.0.1", 12345)
    client1.setWindowTitle("Chat Klient 1")
    client1.move(50, 50)
    client1.show()
    
    # Klient 2 konfigurace
    create_test_config("client", "Klient2")
    client2 = ChatWidget("Klient2", "127.0.0.1", 12345)
    client2.setWindowTitle("Chat Klient 2")
    client2.move(500, 50)
    client2.show()
    
    print("=== Test chat spuštěn - zkuste posílat zprávy ===")
    app.exec()

if __name__ == "__main__":
    test_fixed_chat()

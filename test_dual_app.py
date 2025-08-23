#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test dvou instancí hlavní aplikace
"""

import sys
import os
import subprocess
import time
import json

# Přidání cesty k projektovému adresáři
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PySide6.QtWidgets import QApplication
from views.hlavni_okno import HlavniOkno

def create_server_config():
    """Vytvoří konfiguraci pro server"""
    config_path = os.path.join("chat", "chat_config.json")
    server_config = {
        "mode": "server",
        "server_ip": "0.0.0.0",
        "server_port": 12345,
        "auto_start_server": True,
        "username": "ServerApp"
    }
    
    with open(config_path, 'w') as f:
        json.dump(server_config, f, indent=4)
    print("Server konfigurace vytvořena")

def create_client_config():
    """Vytvoří konfiguraci pro klienta"""
    config_path = os.path.join("chat", "chat_config.json")
    client_config = {
        "mode": "client",
        "server_ip": "127.0.0.1",
        "server_port": 12345,
        "auto_start_server": False,
        "username": "ClientApp"
    }
    
    with open(config_path, 'w') as f:
        json.dump(client_config, f, indent=4)
    print("Client konfigurace vytvořena")

def test_server_app():
    """Spustí aplikaci jako server"""
    print("=== SPOUŠTÍM SERVER APLIKACI ===")
    create_server_config()
    
    app = QApplication(sys.argv)
    okno = HlavniOkno()
    okno.setWindowTitle("Chat Server App")
    okno.show()
    
    app.exec()

def test_client_app():
    """Spustí aplikaci jako klient"""
    print("=== SPOUŠTÍM CLIENT APLIKACI ===")
    create_client_config()
    
    app = QApplication(sys.argv)
    okno = HlavniOkno()
    okno.setWindowTitle("Chat Client App")
    okno.move(600, 50)  # Posunout okno
    okno.show()
    
    app.exec()

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "client":
        test_client_app()
    else:
        test_server_app()

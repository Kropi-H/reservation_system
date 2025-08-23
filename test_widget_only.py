#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test pouze chat widget
"""

import sys
import os

# Přidání cesty k projektovému adresáři
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PySide6.QtWidgets import QApplication
from chat.chat_widget import ChatWidget

def test_widget_only():
    """Test pouze chat widgetu"""
    app = QApplication(sys.argv)
    
    print("=== TEST CHAT WIDGET ===")
    
    # Změníme konfiguraci na klient režim
    import json
    config_path = os.path.join("chat", "chat_config.json")
    with open(config_path, 'w') as f:
        json.dump({
            "mode": "client",
            "server_ip": "127.0.0.1",
            "server_port": 12345,
            "auto_start_server": False,
            "username": "TestWidget"
        }, f, indent=4)
    
    chat = ChatWidget("TestWidget", "127.0.0.1", 12345)
    chat.show()
    
    app.exec()

if __name__ == "__main__":
    test_widget_only()

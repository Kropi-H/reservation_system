#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Jednoduchý test chat server
"""

import sys
import os
import json

# Přidání cesty k projektovému adresáři
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from chat.chat_server import ChatServer

def test_server():
    print("=== SPOUŠTÍM CHAT SERVER ===")
    
    # Nastavení konfigurace pro server
    config_path = os.path.join("chat", "chat_config.json")
    server_config = {
        "mode": "server",
        "server_ip": "0.0.0.0",
        "server_port": 12345,
        "auto_start_server": True,
        "username": "Server"
    }
    
    with open(config_path, 'w') as f:
        json.dump(server_config, f, indent=4)
    
    print("Konfigurace serveru nastavena")
    
    server = ChatServer()
    try:
        server.start()
    except KeyboardInterrupt:
        print("\n=== UKONČUJI SERVER ===")
        server.stop()
    except Exception as e:
        print(f"Server error: {e}")

if __name__ == "__main__":
    test_server()

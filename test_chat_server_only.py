#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test chat server samostatně
"""

import sys
import os

# Přidání cesty k projektovému adresáři
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from chat.chat_server import ChatServer

def test_chat_server():
    """Spustí chat server pro testování"""
    print("Spouštím chat server pro testování...")
    server = ChatServer()
    try:
        server.start()
    except KeyboardInterrupt:
        print("\nUkončuji server...")
        server.stop()

if __name__ == "__main__":
    test_chat_server()

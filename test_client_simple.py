#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Jednoduchý test chat klient
"""

import sys
import os

# Přidání cesty k projektovému adresáři
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PySide6.QtWidgets import QApplication
from chat.chat_widget import ChatWidget

def test_client():
    app = QApplication(sys.argv)
    
    print("=== SPOUŠTÍM CHAT KLIENT ===")
    chat = ChatWidget("TestKlient", "127.0.0.1", 12345)
    chat.show()
    
    app.exec()

if __name__ == "__main__":
    test_client()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test konfigurační dialog pro chat
"""

import sys
import os

# Přidání cesty k projektovému adresáři
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PySide6.QtWidgets import QApplication
from views.chat_config_dialog import ChatConfigDialog

def test_chat_config_dialog():
    app = QApplication(sys.argv)
    
    dialog = ChatConfigDialog()
    
    if dialog.exec():
        config = dialog.get_config()
        print("Uložená konfigurace:")
        for key, value in config.items():
            print(f"  {key}: {value}")
    else:
        print("Dialog byl zrušen")

if __name__ == "__main__":
    test_chat_config_dialog()

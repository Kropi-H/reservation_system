#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test chat funkcionality - spustí server a několik klientů
"""

import sys
import os
import time
import subprocess
import threading

# Přidání cesty k projektovému adresáři
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PySide6.QtWidgets import QApplication, QVBoxLayout, QWidget, QPushButton, QLabel
from PySide6.QtCore import QTimer
from chat.chat_widget import ChatWidget

class ChatTestWindow(QWidget):
    def __init__(self, mode="client", username="Test"):
        super().__init__()
        self.setWindowTitle(f"Chat Test - {mode} - {username}")
        self.setGeometry(100, 100, 400, 600)
        
        layout = QVBoxLayout()
        
        # Info label
        info = QLabel(f"Režim: {mode}\nUživatel: {username}")
        layout.addWidget(info)
        
        # Chat widget
        if mode == "server":
            self.chat = ChatWidget(username, "127.0.0.1", 12345)
        else:
            self.chat = ChatWidget(username, "127.0.0.1", 12345)
            
        layout.addWidget(self.chat)
        
        self.setLayout(layout)

def test_chat_functionality():
    """Otestuje chat funkcionalita"""
    app = QApplication(sys.argv)
    
    # Vytvoření test oken
    server_window = ChatTestWindow("server", "Server")
    client1_window = ChatTestWindow("client", "Klient1") 
    client2_window = ChatTestWindow("client", "Klient2")
    
    # Umístění oken vedle sebe
    server_window.move(50, 50)
    client1_window.move(500, 50)
    client2_window.move(950, 50)
    
    # Zobrazení oken
    server_window.show()
    client1_window.show()
    client2_window.show()
    
    app.exec()

if __name__ == "__main__":
    test_chat_functionality()

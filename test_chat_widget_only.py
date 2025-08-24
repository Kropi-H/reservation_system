#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Test pouze ChatWidget komponenty
"""
import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from chat.chat_widget import ChatWidget

class TestWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Test Chat Widget")
        self.setGeometry(100, 100, 400, 300)
        
        # Vytvořím central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout
        layout = QVBoxLayout()
        
        # Chat widget
        self.chat_widget = ChatWidget(username="TestUser")
        layout.addWidget(self.chat_widget)
        
        central_widget.setLayout(layout)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    print("Spouštím test ChatWidget...")
    window = TestWindow()
    window.show()
    
    try:
        sys.exit(app.exec())
    except KeyboardInterrupt:
        print("\nTest ukončen")

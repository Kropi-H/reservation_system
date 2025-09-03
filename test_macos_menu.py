#!/usr/bin/env python3
"""
Jednoduchý test pro ověření macOS menu
"""

import sys
import platform
from PySide6.QtWidgets import QApplication, QMainWindow, QMenuBar, QAction

class TestWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Test macOS Menu")
        self.setGeometry(300, 300, 400, 200)
        
        # Vytvoření menu baru
        self.menu_bar = QMenuBar(self)
        
        print(f"🖥️ OS: {platform.system()}")
        
        if platform.system() == "Darwin":  # macOS
            print("🍎 Vytváření macOS menu...")
            self.menu_bar.setNativeMenuBar(True)
            
            # Hlavní menu aplikace
            app_menu = self.menu_bar.addMenu("TestApp")
            
            test_action = QAction("Test Action", self)
            test_action.triggered.connect(self.test_click)
            app_menu.addAction(test_action)
            
            app_menu.addSeparator()
            quit_action = QAction("Quit TestApp", self)
            quit_action.setShortcut("Cmd+Q")
            quit_action.triggered.connect(self.close)
            app_menu.addAction(quit_action)
            
            print("🍎 Menu vytvořeno - hledejte 'TestApp' v horní liště")
        else:
            print("🖥️ Vytváření standardního menu...")
            self.menu_bar.setNativeMenuBar(False)
            
            test_action = QAction("Test Action", self)
            test_action.triggered.connect(self.test_click)
            self.menu_bar.addAction(test_action)
        
        self.setMenuBar(self.menu_bar)
    
    def test_click(self):
        print("✅ Menu akce funguje!")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Nastavení názvu aplikace
    app.setApplicationName("TestApp")
    app.setApplicationDisplayName("Test Application")
    
    window = TestWindow()
    window.show()
    
    print("🚀 Aplikace spuštěna")
    if platform.system() == "Darwin":
        print("🍎 Na macOS hledejte menu 'TestApp' v horní liště systému!")
    
    sys.exit(app.exec())

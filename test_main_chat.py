#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Test chatu v hlavní aplikaci
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from PySide6.QtWidgets import QApplication
from setup_databaze import setup_database
from views.hlavni_okno import HlavniOkno

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    print("Spouštím hlavní aplikaci s focus na chat...")
    
    # Inicializace databáze
    setup_database()
    
    # Hlavní okno
    main_window = HlavniOkno()
    main_window.show()
    
    # Ihned po startu zobrazím chat
    print("Pokouším se zobrazit chat...")
    if hasattr(main_window, 'checkboxy') and "Chat" in main_window.checkboxy:
        main_window.checkboxy["Chat"].setChecked(True)
        main_window.toggle_chat_visibility(True)
        print("Chat checkbox nastaven na True")
    else:
        print("Chat checkbox nenalezen!")
        print(f"Dostupné checkboxy: {getattr(main_window, 'checkboxy', {}).keys()}")
    
    if hasattr(main_window, 'chat') and main_window.chat:
        print(f"Chat widget existuje: {main_window.chat}")
        print(f"Chat visible: {main_window.chat.isVisible()}")
    else:
        print("Chat widget nenalezen!")
    
    try:
        sys.exit(app.exec())
    except KeyboardInterrupt:
        print("\nAplikace ukončena")

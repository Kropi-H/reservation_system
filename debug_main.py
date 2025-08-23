#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Debug verze hlavní aplikace s detailním logováním chatu
"""

import sys
import os

# Přidání cesty k projektovému adresáři
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PySide6.QtWidgets import QApplication
from views.hlavni_okno import HlavniOkno

class DebugHlavniOkno(HlavniOkno):
    def initialize_chat(self, config):
        """Přepsaná metoda s debug výpisy"""
        print("=== DEBUG: initialize_chat volána ===")
        print(f"Konfigurace: {config}")
        
        try:
            # Určení IP pro klienta
            server_ip = config.get("server_ip", "127.0.0.1")
            if server_ip == "0.0.0.0":
                client_ip = "127.0.0.1"
            else:
                client_ip = server_ip
                
            username = config.get("username", "Uživatel")
            server_port = config.get("server_port", 12345)
            
            print(f"Připojuji se jako: {username} na {client_ip}:{server_port}")
            
            # Import zde pro debug
            from chat.chat_widget import ChatWidget
            
            # Vytvoření chat widgetu
            self.chat = ChatWidget(
                username=username, 
                server_host=client_ip, 
                server_port=server_port
            )
            
            print("Chat widget vytvořen")
            
            # Nastavení velikosti chatu
            self.chat.setMinimumWidth(300)
            self.chat.setMaximumWidth(450)
            
            # Nastavení size policy pro lepší chování
            from PySide6.QtWidgets import QSizePolicy
            self.chat.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
            
            # Přidání chatu do layoutu
            self.ordinace_layout.addWidget(self.chat)
            print("Chat přidán do layoutu")
            
            self.chat_initialized = True
            print("Chat inicializace dokončena")
            
        except Exception as e:
            print(f"=== CHYBA při inicializaci chatu: {e} ===")
            import traceback
            traceback.print_exc()
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.critical(self, "Chyba", f"Nepodařilo se inicializovat chat:\n{str(e)}")
            self.checkboxy["Chat"].setChecked(False)

def main():
    app = QApplication(sys.argv)
    
    print("=== SPOUŠTÍM DEBUG HLAVNÍ OKNO ===")
    okno = DebugHlavniOkno()
    okno.show()
    
    app.exec()

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Test chatu - pokus o spuštění chat widgetu samostatně
"""
import sys
import os

# Přidání cesty k projektu
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    print("Test 1: Import ChatWidget...")
    from chat.chat_widget import ChatWidget
    print("✅ ChatWidget se úspěšně importoval")
    
    print("\nTest 2: Import ChatServer...")
    from chat.chat_server import ChatServer
    print("✅ ChatServer se úspěšně importoval")
    
    print("\nTest 3: Import ChatConfigDialog...")
    from views.chat_config_dialog import ChatConfigDialog
    print("✅ ChatConfigDialog se úspěšně importoval")
    
    print("\nTest 4: Vytvoření instance ChatServer...")
    server = ChatServer()
    print("✅ ChatServer instance vytvořena úspěšně")
    
    print("\n✅ Všechny chat komponenty fungují správně!")
    
except Exception as e:
    print(f"❌ Chyba při testování chatu: {e}")
    import traceback
    traceback.print_exc()

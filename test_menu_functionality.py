#!/usr/bin/env python3
"""
Funkcionální test menu "Změnit databázi" v hlavní aplikaci.
"""

import sys
import time
from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtCore import QTimer

def test_menu_change_database():
    """Test funkcionality menu pro změnu databáze."""
    
    print("🔍 Testování menu 'Změnit databázi'...")
    
    try:
        from views.hlavni_okno import HlavniOkno
        from views.postgresql_setup_dialog import PostgreSQLSetupDialog
        
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        # Vytvoř hlavní okno
        okno = HlavniOkno()
        print("✅ Hlavní okno vytvořeno")
        
        # Simulace přihlášení jako admin (potřebné pro zobrazení menu)
        okno.logged_in_user_role = "admin"
        okno.update_user_menu()
        print("✅ Uživatelské menu aktualizováno (admin role)")
        
        # Ověření existence menu akcí
        if hasattr(okno, 'database_section'):
            print("✅ Menu akce 'Změnit databázi' existuje")
            print(f"   Text akce: '{okno.database_section.text()}'")
        else:
            print("❌ Menu akce 'Změnit databázi' neexistuje")
            return False
        
        # Test volání metody change_database
        if hasattr(okno, 'change_database'):
            print("✅ Metoda change_database() existuje")
            
            # Zde bychom mohli otestovat volání, ale vyžadovalo by to GUI interakci
            print("   Metoda je připravena k použití")
        else:
            print("❌ Metoda change_database() neexistuje")
            return False
        
        # Test existence user_menu
        if okno.user_menu:
            print("✅ User menu existuje")
            actions = okno.user_menu.actions()
            action_texts = [action.text() for action in actions]
            print(f"   Dostupné akce: {action_texts}")
            
            if "Změnit databázi" in action_texts:
                print("✅ Menu obsahuje položku 'Změnit databázi'")
            else:
                print("❌ Menu neobsahuje položku 'Změnit databázi'")
                return False
        else:
            print("❌ User menu neexistuje")
            return False
        
        okno.deleteLater()
        print("✅ Test dokončen úspěšně")
        return True
        
    except Exception as e:
        print(f"❌ Chyba během testu: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_postgresql_dialog_integration():
    """Test integrace PostgreSQL dialogu."""
    
    print("\n🔍 Testování integrace PostgreSQL dialogu...")
    
    try:
        from views.postgresql_setup_dialog import PostgreSQLSetupDialog
        
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        # Test vytvoření dialogu
        dialog = PostgreSQLSetupDialog()
        print("✅ PostgreSQL dialog vytvořen")
        
        # Test načtení aktuální konfigurace
        from config import get_database_config
        current_config = get_database_config()
        if current_config:
            dialog.set_config(current_config)
            print("✅ Aktuální konfigurace načtena do dialogu")
            print(f"   Host: {current_config.get('host', 'N/A')}")
            print(f"   Port: {current_config.get('port', 'N/A')}")
            print(f"   Databáze: {current_config.get('database', 'N/A')}")
            print(f"   Uživatel: {current_config.get('user', 'N/A')}")
        else:
            print("❌ Nepodařilo se načíst aktuální konfiguraci")
            return False
        
        # Test get_config metody
        form_config = dialog.get_config()
        if form_config:
            print("✅ Konfigurace z formuláře získána")
            print(f"   Formulář obsahuje: {list(form_config.keys())}")
        else:
            print("❌ Nepodařilo se získat konfiguraci z formuláře")
            return False
        
        dialog.deleteLater()
        print("✅ Test integrace dokončen úspěšně")
        return True
        
    except Exception as e:
        print(f"❌ Chyba během testu integrace: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Spouštím funkcionální testy menu 'Změnit databázi'")
    print("=" * 60)
    
    tests = [
        ("Menu 'Změnit databázi'", test_menu_change_database),
        ("Integrace PostgreSQL dialogu", test_postgresql_dialog_integration)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n📋 Test: {test_name}")
        print("-" * 40)
        result = test_func()
        results.append(result)
    
    # Souhrn
    passed = sum(results)
    total = len(results)
    
    print("\n" + "=" * 60)
    print("📊 SOUHRN FUNKCIONÁLNÍCH TESTŮ:")
    print(f"Úspěšné: {passed}/{total}")
    
    if passed == total:
        print("🎉 Všechny funkcionální testy prošly úspěšně!")
        print("\n✅ Menu 'Změnit databázi' je připraveno k použití!")
        sys.exit(0)
    else:
        print("⚠️ Některé funkcionální testy selhaly.")
        sys.exit(1)

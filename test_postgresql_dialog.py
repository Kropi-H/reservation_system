#!/usr/bin/env python3
"""
Test skript pro ověření PostgreSQL setup dialogu.
"""

import sys
from PySide6.QtWidgets import QApplication

def test_postgresql_dialog_import():
    """Test importu PostgreSQL setup dialogu."""
    try:
        from views.postgresql_setup_dialog import PostgreSQLSetupDialog
        print("✅ Import PostgreSQLSetupDialog úspěšný")
        return True
    except ImportError as e:
        print(f"❌ Chyba při importu PostgreSQLSetupDialog: {e}")
        return False

def test_postgresql_dialog_creation():
    """Test vytvoření PostgreSQL setup dialogu."""
    try:
        from views.postgresql_setup_dialog import PostgreSQLSetupDialog
        
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        dialog = PostgreSQLSetupDialog()
        print("✅ Vytvoření PostgreSQLSetupDialog úspěšné")
        print(f"   Název okna: {dialog.windowTitle()}")
        print(f"   Velikost: {dialog.size().width()}x{dialog.size().height()}")
        
        # Test základních metod
        config = dialog.get_config()
        print(f"   Test get_config(): {bool(config)}")
        
        # Test is_connection_successful metody
        success_status = dialog.is_connection_successful()
        print(f"   Test is_connection_successful(): {success_status}")
        
        dialog.deleteLater()
        return True
        
    except Exception as e:
        print(f"❌ Chyba při vytváření PostgreSQLSetupDialog: {e}")
        return False

def test_hlavni_okno_import():
    """Test importu hlavního okna s novou funkcionalitou."""
    try:
        from views.hlavni_okno import HlavniOkno
        print("✅ Import HlavniOkno s PostgreSQL podporou úspěšný")
        return True
    except ImportError as e:
        print(f"❌ Chyba při importu HlavniOkno: {e}")
        return False

if __name__ == "__main__":
    print("🔍 Testování PostgreSQL setup dialog integrace...")
    print()
    
    tests = [
        ("Import PostgreSQL dialogu", test_postgresql_dialog_import),
        ("Vytvoření PostgreSQL dialogu", test_postgresql_dialog_creation),
        ("Import hlavního okna", test_hlavni_okno_import)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"Spouštím test: {test_name}")
        result = test_func()
        results.append(result)
        print()
    
    # Souhrn
    passed = sum(results)
    total = len(results)
    
    print("=" * 50)
    print("SOUHRN TESTŮ:")
    print(f"Úspěšné: {passed}/{total}")
    
    if passed == total:
        print("🎉 Všechny testy prošly úspěšně!")
        sys.exit(0)
    else:
        print("⚠️ Některé testy selhaly.")
        sys.exit(1)

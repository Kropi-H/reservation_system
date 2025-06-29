#!/usr/bin/env python3

import sys
import os

# Přidej aktuální adresář do sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_config():
    """Test konfiguračních funkcí"""
    print("=== TEST KONFIGURACE ===")
    
    try:
        import config
        print("✓ Import config modulu OK")
        
        # Test načítání cesty z konfigurace
        path = config.get_database_path_from_config()
        print(f"✓ Cesta z konfigurace: '{path}'")
        
        # Test posledního adresáře
        last_dir = config.get_last_directory()
        print(f"✓ Poslední adresář: '{last_dir}'")
        
    except Exception as e:
        print(f"✗ Chyba v config: {e}")
        import traceback
        traceback.print_exc()

def test_database():
    """Test databázových funkcí"""
    print("\n=== TEST DATABÁZE ===")
    
    try:
        from models.databaze import get_database_path, database_exists, set_database_path
        print("✓ Import databáze OK")
        
        # Test získání cesty
        path = get_database_path()
        print(f"✓ Aktuální cesta: '{path}'")
        
        # Test existence
        exists = database_exists()
        print(f"✓ Databáze existuje: {exists}")
        
        # Test nastavení cesty
        test_path = "/tmp/test_db.db"
        set_database_path(test_path)
        new_path = get_database_path()
        print(f"✓ Nová cesta nastavena: '{new_path}'")
        
        # Obnovení původní cesty
        set_database_path(path)
        print("✓ Původní cesta obnovena")
        
    except Exception as e:
        print(f"✗ Chyba v databázi: {e}")
        import traceback
        traceback.print_exc()

def test_dialog():
    """Test dialogu pro nastavení databáze"""
    print("\n=== TEST DIALOGU ===")
    
    try:
        from views.database_setup_dialog import DatabaseSetupDialog
        print("✓ Import dialogu OK")
        
    except Exception as e:
        print(f"✗ Chyba v dialogu: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("SPOUŠTÍM TESTY APLIKACE...")
    
    test_config()
    test_database() 
    test_dialog()
    
    print("\n=== VŠECHNY TESTY DOKONČENY ===")

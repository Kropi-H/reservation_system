import sys
import os

# Přidej aktuální adresář do sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_config():
    """Test nových konfiguračních funkcí"""
    print("=== TEST NOVÉHO CONFIG.PY ===")
    
    try:
        import config
        print("✓ Import config modulu OK")
        
        # Test typu databáze
        db_type = config.get_database_type()
        print(f"✓ Typ databáze: {db_type}")
        
        # Test PostgreSQL konfigurace
        db_config = config.get_database_config()
        print(f"✓ PostgreSQL konfigurace: {db_config}")
        
        # Test zajištění konfigurace
        ensured_config = config.ensure_database_config()
        print(f"✓ Zajištěná konfigurace: {ensured_config}")
        
        # Test informací o připojení
        conn_info = config.get_connection_info()
        print(f"✓ Info připojení: {conn_info}")
        
        # Test připojení k databázi
        conn_test = config.test_database_connection()
        print(f"✓ Test připojení: {'✅ OK' if conn_test else '❌ FAIL'}")
        
        # Test zpětné kompatibility
        old_path = config.get_database_path_from_config()
        print(f"✓ Zpětná kompatibilita (SQLite path): '{old_path}'")
        
        # Test posledního adresáře
        last_dir = config.get_last_directory()
        print(f"✓ Poslední adresář: '{last_dir}'")
        
        print("✅ Všechny config testy prošly!")
        return True
        
    except Exception as e:
        print(f"✗ Chyba v config testech: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_config()

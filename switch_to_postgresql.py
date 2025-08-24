import sys
import os

# Přidej aktuální adresář do sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def switch_to_postgresql():
    """Přepne konfiguraci na PostgreSQL"""
    print("=== PŘEPÍNÁM NA POSTGRESQL ===")
    
    try:
        import config
        
        # Nastavení PostgreSQL konfigurace
        postgresql_config = {
            "host": "192.168.0.118",
            "port": 5432,
            "database": "veterina",
            "user": "postgres",
            "password": "motodevka25"
        }
        
        # Uložení PostgreSQL konfigurace
        config.save_database_config(postgresql_config)
        print("✓ PostgreSQL konfigurace uložena")
        
        # Nastavení typu databáze
        config.set_database_type('postgresql')
        print("✓ Typ databáze nastaven na PostgreSQL")
        
        # Test konfigurace
        db_type = config.get_database_type()
        print(f"✓ Nový typ databáze: {db_type}")
        
        db_config = config.get_database_config()
        print(f"✓ PostgreSQL konfigurace: {db_config}")
        
        conn_info = config.get_connection_info()
        print(f"✓ Info připojení: {conn_info}")
        
        # Test připojení
        conn_test = config.test_database_connection()
        print(f"✓ Test PostgreSQL připojení: {'✅ OK' if conn_test else '❌ FAIL'}")
        
        if conn_test:
            print("✅ Úspěšně přepnuto na PostgreSQL!")
        else:
            print("⚠️  Konfigurace uložena, ale připojení selhalo")
            
        return conn_test
        
    except Exception as e:
        print(f"✗ Chyba při přepínání: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    switch_to_postgresql()

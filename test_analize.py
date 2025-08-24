import psycopg2
from psycopg2.extras import RealDictCursor

def test_postgresql():
    """Test základního připojení k PostgreSQL"""
    print("🔍 Testování PostgreSQL připojení...")
    
    # Základní konfigurace pro test
    config = {
        "host": "localhost",
        "port": 5432,
        "database": "veterina",
        "user": "postgres",
        "password": "motodevka25"
    }
    
    try:
        print(f"Připojuji se k {config['host']}:{config['port']}")
        conn = psycopg2.connect(**config)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        cursor.execute("SELECT version()")
        version = cursor.fetchone()
        print(f"✅ PostgreSQL připojení OK")
        print(f"✅ Verze: {version['version']}")
        
        cursor.close()
        conn.close()
        
        # Nové připojení pro vytvoření databáze (s autocommit)
        config_postgres = config.copy()
        config_postgres['database'] = 'postgres'
        
        conn = psycopg2.connect(**config_postgres)
        conn.autocommit = True
        cursor = conn.cursor()
        
        cursor.execute("SELECT 1 FROM pg_database WHERE datname = 'reservation_system_test'")
        if not cursor.fetchone():
            cursor.execute("CREATE DATABASE reservation_system_test")
            print("✅ Testovací databáze vytvořena")
        else:
            print("✅ Testovací databáze již existuje")
            
        cursor.close()
        conn.close()
        
        print("✅ Všechny testy PostgreSQL prošly!")
        return True
        
    except psycopg2.OperationalError as e:
        print(f"❌ Chyba připojení: {e}")
        return False
    except Exception as e:
        print(f"❌ Neočekávaná chyba: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_postgresql()
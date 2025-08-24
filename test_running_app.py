import sys
import os

# Přidej aktuální adresář do sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_database_operations():
    """Test základních databázových operací zatímco běží aplikace"""
    print("=== TEST DATABÁZOVÝCH OPERACÍ ===")
    
    try:
        from models import databaze, doktori, ordinace, rezervace, settings, users
        
        print("1. Test dostupnosti databáze...")
        exists = databaze.database_exists()
        print(f"✓ Databáze dostupná: {exists}")
        
        print("2. Test základních dotazů...")
        
        # Test doktorů
        doktori_list = databaze.get_doktori()
        print(f"✓ Počet doktorů: {len(doktori_list)}")
        
        # Test ordinací
        ordinace_list = databaze.get_ordinace()
        print(f"✓ Počet ordinací: {len(ordinace_list)}")
        for ord in ordinace_list:
            print(f"  - {ord}")
        
        # Test settings
        days_setting = settings.get_settings("days_to_keep")
        print(f"✓ Nastavení days_to_keep: {days_setting}")
        
        print("3. Test struktury databáze...")
        
        with databaze.get_connection() as conn:
            cur = conn.cursor()
            
            # Zjisti, jaké tabulky existují
            cur.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name
            """)
            tables = cur.fetchall()
            print(f"✓ Existující tabulky ({len(tables)}):")
            for table in tables:
                print(f"  - {table[0]}")
                
            # Test struktury tabulky Doktori
            cur.execute("""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns 
                WHERE table_name = 'doktori' 
                ORDER BY ordinal_position
            """)
            columns = cur.fetchall()
            print(f"✓ Struktura tabulky Doktori ({len(columns)} sloupců):")
            for col in columns:
                print(f"  - {col[0]}: {col[1]} ({'NULL' if col[2] == 'YES' else 'NOT NULL'})")
        
        print("✅ Všechny databázové testy prošly!")
        return True
        
    except Exception as e:
        print(f"✗ Chyba při testování: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_database_operations()

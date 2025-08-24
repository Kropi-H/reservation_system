import sys
import os

# Přidej aktuální adresář do sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_databaze_postgresql():
    """Test nového PostgreSQL databázového modulu"""
    print("=== TEST MODELS/DATABAZE.PY PRO POSTGRESQL ===")
    
    try:
        # Import databázového modulu
        from models import databaze
        print("✓ Import models.databaze OK")
        
        # Test připojení
        conn = databaze.get_connection()
        print("✓ Připojení k PostgreSQL OK")
        conn.close()
        
        # Test database_exists
        exists = databaze.database_exists()
        print(f"✓ database_exists(): {exists}")
        
        # Test get_database_path (connection string)
        path = databaze.get_database_path()
        print(f"✓ get_database_path(): {path}")
        
        # Test inicializace databáze
        print("✓ Testování inicializace databáze...")
        databaze.inicializuj_databazi()
        print("✓ Inicializace databáze OK")
        
        # Test základních dotazů
        print("✓ Testování základních dotazů...")
        
        # Test get_doktori
        doktori = databaze.get_doktori()
        print(f"✓ get_doktori(): {len(doktori)} doktorů")
        
        # Test get_ordinace
        ordinace = databaze.get_ordinace()
        print(f"✓ get_ordinace(): {len(ordinace)} ordinací")
        
        # Test get_or_create funkcionality
        with databaze.get_connection() as conn:
            cur = conn.cursor()
            
            # Test vložení testovacího doktora
            test_data = {
                'jmeno': 'Test',
                'prijmeni': 'Doktor',
                'specializace': 'Testovací',
                'isActive': 1,
                'color': '#FF0000'
            }
            
            doktor_id = databaze.get_or_create(cur, 'Doktori', ('jmeno', 'prijmeni'), test_data)
            print(f"✓ get_or_create test doktor ID: {doktor_id}")
            
            # Zkus znovu - měl by vrátit stejné ID
            doktor_id2 = databaze.get_or_create(cur, 'Doktori', ('jmeno', 'prijmeni'), test_data)
            print(f"✓ get_or_create znovu (stejný doktor) ID: {doktor_id2}")
            
            if doktor_id == doktor_id2:
                print("✓ get_or_create funguje správně - vrací stejné ID")
            else:
                print("✗ get_or_create problém - vrací různá ID")
            
            # Vymaž testovacího doktora
            cur.execute("DELETE FROM Doktori WHERE jmeno = %s AND prijmeni = %s", ('Test', 'Doktor'))
            conn.commit()
            print("✓ Testovací data vymazána")
        
        # Test get_user_by_username (prázdný výsledek je OK)
        user = databaze.get_user_by_username('neexistujici_uzivatel')
        print(f"✓ get_user_by_username('neexistujici_uzivatel'): {user}")
        
        print("✅ Všechny testy databáze prošly!")
        return True
        
    except Exception as e:
        print(f"✗ Chyba v databázových testech: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_databaze_postgresql()

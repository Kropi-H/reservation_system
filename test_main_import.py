import sys
import os
import traceback

# Přidej aktuální adresář do sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_main_import():
    """Test postupného importu částí aplikace"""
    print("=== TEST POSTUPNÉHO IMPORTU APLIKACE ===")
    
    try:
        print("1. Testování importu config...")
        import config
        print("✓ Config import OK")
        
        print("2. Testování importu models.databaze...")
        from models import databaze
        print("✓ Models.databaze import OK")
        
        print("3. Testování importu models.settings...")
        from models import settings
        print("✓ Models.settings import OK")
        
        print("4. Testování get_settings funkce...")
        result = settings.get_settings("days_to_keep")
        print(f"✓ get_settings('days_to_keep'): {result}")
        
        print("5. Testování importu PySide6...")
        from PySide6.QtWidgets import QApplication
        print("✓ PySide6 import OK")
        
        print("6. Testování importu views.hlavni_okno...")
        from views.hlavni_okno import HlavniOkno
        print("✓ Views.hlavni_okno import OK")
        
        print("7. Testování vytvoření QApplication...")
        app = QApplication(sys.argv)
        print("✓ QApplication vytvořena OK")
        
        print("8. Testování vytvoření hlavního okna...")
        window = HlavniOkno()
        print("✓ HlavniOkno vytvořeno OK")
        
        print("✅ Všechny testy prošly!")
        return True
        
    except Exception as e:
        print(f"✗ Chyba při testu: {e}")
        print("\n=== TRACEBACK ===")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_main_import()

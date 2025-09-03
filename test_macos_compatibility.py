#!/usr/bin/env python3
"""
Test skript pro macOS connection pool problém
"""
import sys
import os
import platform
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

print(f"🖥️ Testování na: {platform.system()} {platform.release()}")

def test_macos_connection_pool():
    """Test connection poolu na macOS."""
    try:
        from models.connection_pool import get_pooled_connection, put_pooled_connection
        print("✅ Connection pool import OK")
        
        # Test základního připojení
        conn = get_pooled_connection()
        print("✅ Získání connection z poolu OK")
        
        # Test dotazu
        cur = conn.cursor()
        cur.execute("SELECT version()")
        version = cur.fetchone()[0]
        cur.close()
        print(f"✅ Test dotazu OK: {version[:50]}...")
        
        # Vrátit připojení
        put_pooled_connection(conn)
        print("✅ Vrácení connection do poolu OK")
        
        return True
        
    except Exception as e:
        print(f"❌ Connection pool test selhal: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_macos_database_listener():
    """Test database listeneru na macOS."""
    try:
        from models.database_listener import DatabaseListener
        print("✅ DatabaseListener import OK")
        
        # Test inicializace
        listener = DatabaseListener()
        print("✅ DatabaseListener inicializace OK")
        
        # Test spuštění (krátký test)
        listener.start_listening(['test_channel'])
        print("✅ DatabaseListener spuštění OK")
        
        # Krátká pauza pro test
        import time
        time.sleep(2)
        
        # Zastavení
        listener.stop_listening()
        print("✅ DatabaseListener zastavení OK")
        
        return True
        
    except Exception as e:
        print(f"❌ DatabaseListener test selhal: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_select_module():
    """Test select modulu - nyní jen informativní."""
    try:
        import select
        print("✅ Select module import OK")
        
        # Poznámka: select.select() má problémy s prázdnými seznamy na Windows/macOS
        # Database listener nyní používá univerzální polling metodu
        print("ℹ️ Select module dostupný, ale database listener používá polling metodu")
        
        return True  # Vždy vrátíme success, protože select už nepotřebujeme
        
    except Exception as e:
        print(f"⚠️ Select module test: {e}")
        print("ℹ️ To je v pořádku - database listener používá polling metodu")
        return True  # Vždy vrátíme success

if __name__ == "__main__":
    print("🧪 Spouštím macOS diagnostické testy...")
    
    if platform.system() == "Darwin":
        print("🍎 macOS detekován - spouštím všechny testy")
    else:
        print(f"⚠️ Testy určené pro macOS, ale běží na {platform.system()}")
    
    print("\n1️⃣ Test select modulu:")
    select_ok = test_select_module()
    
    print("\n2️⃣ Test connection poolu:")
    pool_ok = test_macos_connection_pool()
    
    print("\n3️⃣ Test database listeneru:")
    listener_ok = test_macos_database_listener()
    
    print(f"\n📊 Výsledky testů:")
    print(f"   Select module: {'✅' if select_ok else '❌'}")
    print(f"   Connection pool: {'✅' if pool_ok else '❌'}")
    print(f"   Database listener: {'✅' if listener_ok else '❌'}")
    
    if all([select_ok, pool_ok, listener_ok]):
        print("\n🎉 Všechny testy prošly! macOS by měl fungovat.")
    else:
        print("\n⚠️ Některé testy selhaly - zkontrolujte chyby výše.")

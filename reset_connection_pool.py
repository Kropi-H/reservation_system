#!/usr/bin/env python3
"""
Emergency script pro reset connection poolu
Použij když se objeví "connection pool exhausted" chyba
"""

def reset_pool():
    """Resetuje connection pool"""
    try:
        from models.connection_pool import reset_connection_pool
        print("🔄 Resetuji connection pool...")
        reset_connection_pool()
        print("✅ Connection pool byl resetován")
        return True
    except Exception as e:
        print(f"❌ Chyba při resetování poolu: {e}")
        return False

def test_connection():
    """Testuje připojení po resetu"""
    try:
        from models.databaze import get_connection
        print("🔍 Testuji připojení...")
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM users")
            count = cur.fetchone()[0]
            print(f"✅ Připojení OK - počet uživatelů: {count}")
        return True
    except Exception as e:
        print(f"❌ Chyba při testování: {e}")
        return False

if __name__ == "__main__":
    print("=== CONNECTION POOL RESET ===")
    
    # 1. Reset poolu
    if reset_pool():
        # 2. Test připojení
        if test_connection():
            print("\n🎉 Connection pool úspěšně resetován a testován!")
            print("Aplikace by měla nyní fungovat normálně.")
        else:
            print("\n⚠️ Pool resetován, ale test připojení selhal.")
    else:
        print("\n❌ Reset poolu selhal.")
    
    print("\nMůžete nyní spustit aplikaci: python main.py")

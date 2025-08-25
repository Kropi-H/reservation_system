#!/usr/bin/env python3
"""
Rychlý test připojení k PostgreSQL serveru 192.168.0.118
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import socket
import psycopg2
from config import test_database_connection, save_database_config

def test_network_connectivity():
    """Test síťové konektivity na server."""
    print("🔍 Testování síťové konektivity k 192.168.0.118:5432...")
    
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex(('192.168.0.118', 5432))
        sock.close()
        
        if result == 0:
            print("✅ Síťové připojení na port 5432 je funkční")
            return True
        else:
            print("❌ Síťové připojení na port 5432 selhalo")
            return False
    except Exception as e:
        print(f"❌ Chyba při testu síťové konektivity: {e}")
        return False

def test_postgresql_connection():
    """Test PostgreSQL připojení."""
    print("\n🔍 Testování PostgreSQL připojení k 192.168.0.118...")
    
    # Standardní konfigurace
    config = {
        'host': '192.168.0.118',
        'port': 5432,
        'database': 'veterina',
        'user': 'postgres',
        'password': 'motodevka25'  # Změňte podle potřeby
    }
    
    print(f"   Server: {config['host']}:{config['port']}")
    print(f"   Databáze: {config['database']}")
    print(f"   Uživatel: {config['user']}")
    
    try:
        conn = psycopg2.connect(**config)
        cursor = conn.cursor()
        
        # Test základního dotazu
        cursor.execute("SELECT version()")
        version = cursor.fetchone()[0]
        print(f"✅ PostgreSQL připojení je funkční")
        print(f"✅ Verze: {version}")
        
        # Test aplikačních tabulek
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name IN ('doktori', 'ordinace', 'rezervace', 'pacienti')
        """)
        tables = cursor.fetchall()
        
        if tables:
            print(f"✅ Nalezeno {len(tables)} aplikačních tabulek:")
            for table in tables:
                print(f"   - {table[0]}")
        else:
            print("⚠️ Aplikační tabulky nebyly nalezeny")
            print("💡 Možná je potřeba spustit inicializaci databáze")
        
        cursor.close()
        conn.close()
        
        # Nabídka uložení konfigurace
        save_config = input("\nUložit tuto konfiguraci jako výchozí? (Y/n): ")
        if save_config.lower() != 'n':
            save_database_config(config)
            print("✅ Konfigurace byla uložena jako výchozí")
        
        return True
        
    except psycopg2.OperationalError as e:
        error_msg = str(e)
        print(f"❌ PostgreSQL připojení selhalo")
        
        if "could not connect to server" in error_msg:
            print("💡 Možné příčiny:")
            print("   • PostgreSQL server na 192.168.0.118 není spuštěn")
            print("   • Firewall blokuje port 5432")
            print("   • listen_addresses v postgresql.conf není nastaveno na '*'")
        elif "authentication failed" in error_msg:
            print("💡 Možné příčiny:")
            print("   • Nesprávné uživatelské jméno nebo heslo")
            print("   • pg_hba.conf nepovoluje připojení z vaší IP")
        elif "database" in error_msg and "does not exist" in error_msg:
            print("💡 Možné příčiny:")
            print("   • Databáze 'veterina' neexistuje na serveru")
            print("   • Potřeba vytvořit databázi: CREATE DATABASE veterina;")
        
        print(f"\n📋 Detaily chyby: {error_msg}")
        return False
    
    except Exception as e:
        print(f"❌ Neočekávaná chyba: {e}")
        return False

def main():
    print("=== RYCHLÝ TEST PŘIPOJENÍ K POSTGRESQL SERVERU ===")
    print("Server: 192.168.0.118:5432")
    print("Databáze: veterina")
    print("-" * 55)
    
    # Test síťové konektivity
    if not test_network_connectivity():
        print("\n💡 Řešení síťových problémů:")
        print("1. Zkontrolujte, zda je server 192.168.0.118 zapnutý")
        print("2. Ověřte síťové připojení: ping 192.168.0.118")
        print("3. Zkontrolujte firewall na serveru (port 5432)")
        print("4. Ověřte postgresql.conf: listen_addresses = '*'")
        return
    
    # Test PostgreSQL připojení
    if test_postgresql_connection():
        print("\n🎉 Všechny testy prošly úspěšně!")
        print("Aplikace je připravena pro použití se serverem 192.168.0.118")
        
        print("\n📝 Další kroky:")
        print("1. Spusťte aplikaci: python main.py")
        print("2. Nebo použijte network manager: python network_config_manager.py")
    else:
        print("\n⚠️ Připojení k PostgreSQL serveru selhalo")
        print("\n📝 Doporučené kroky:")
        print("1. Zkontrolujte PostgreSQL konfiguraci na serveru")
        print("2. Ověřte přihlašovací údaje")
        print("3. Zkontrolujte existenci databáze 'veterina'")

if __name__ == "__main__":
    main()

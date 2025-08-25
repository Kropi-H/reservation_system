#!/usr/bin/env python3
"""
Rychlý test ověření IP adresy 192.168.0.118 v konfiguraci
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import get_database_config, get_network_database_configs, get_connection_info

def main():
    print("=== OVĚŘENÍ KONFIGURACE SERVERU 192.168.0.118 ===\n")
    
    # Zkontroluj aktuální konfiguraci
    print("📋 Aktuální databázová konfigurace:")
    current_config = get_database_config()
    if current_config:
        print(f"   Host: {current_config['host']}")
        print(f"   Port: {current_config['port']}")
        print(f"   Database: {current_config['database']}")
        print(f"   User: {current_config['user']}")
        
        if current_config['host'] == '192.168.0.118':
            print("   ✅ IP adresa je správně nastavena na 192.168.0.118")
        else:
            print(f"   ❌ IP adresa je {current_config['host']}, měla by být 192.168.0.118")
    else:
        print("   ❌ Žádná konfigurace nenalezena")
    
    # Zkontroluj síťové konfigurace
    print("\n📋 Síťové konfigurace:")
    network_configs = get_network_database_configs()
    if network_configs:
        for name, config in network_configs.items():
            print(f"   {name}: {config['host']}:{config['port']}")
            if name == 'server' and config['host'] == '192.168.0.118':
                print("   ✅ Server konfigurace má správnou IP")
    else:
        print("   ❌ Žádné síťové konfigurace nenalezeny")
    
    # Zobraz connection info
    print(f"\n📡 Connection info: {get_connection_info()}")
    
    print("\n🎯 Výsledek:")
    if current_config and current_config['host'] == '192.168.0.118':
        print("✅ Konfigurace je správně nastavena pro server 192.168.0.118")
        print("\n📝 Další kroky:")
        print("1. Test připojení: python test_server_connection.py")
        print("2. Správa konfigurací: python network_config_manager.py")
        print("3. Spuštění aplikace: python main.py")
    else:
        print("❌ Konfigurace není správně nastavena")
        print("💡 Spusťte: python network_config_manager.py")

if __name__ == "__main__":
    main()

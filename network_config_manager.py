#!/usr/bin/env python3
"""
Utility pro správu síťových databázových konfigurací
Použití: python network_config_manager.py
Server IP: 192.168.0.118
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import (
    get_network_database_configs, save_network_database_config,
    set_active_network_config, get_active_network_config_name,
    test_database_connection, test_all_network_configs,
    auto_detect_best_config, get_connection_info, create_default_configs
)

def show_menu():
    """Zobrazí hlavní menu."""
    print("\n=== SPRÁVA SÍŤOVÝCH DATABÁZOVÝCH KONFIGURACÍ ===")
    print("PostgreSQL Server: 192.168.0.118")
    print("-" * 50)
    print("1. Zobrazit všechny konfigurace")
    print("2. Přidat novou konfiguraci")
    print("3. Testovat všechny konfigurace")
    print("4. Nastavit aktivní konfiguraci")
    print("5. Automaticky najít nejlepší konfiguraci")
    print("6. Zobrazit aktuální připojení")
    print("7. Odstranit konfiguraci")
    print("8. Vytvořit výchozí konfigurace")
    print("9. Test připojení k serveru 192.168.0.118")
    print("0. Ukončit")
    print("-" * 50)

def show_configurations():
    """Zobrazí všechny uložené konfigurace."""
    configs = get_network_database_configs()
    active_name = get_active_network_config_name()
    
    if not configs:
        print("❌ Žádné konfigurace nenalezeny")
        print("💡 Spusťte volbu 8 pro vytvoření výchozích konfigurací")
        return
    
    print("\n📋 Uložené konfigurace:")
    for name, config in configs.items():
        status = " (AKTIVNÍ)" if name == active_name else ""
        print(f"  • {name}{status}")
        print(f"    {config['user']}@{config['host']}:{config['port']}/{config['database']}")

def add_configuration():
    """Přidá novou síťovou konfiguraci."""
    print("\n➕ Přidání nové konfigurace:")
    
    name = input("Název konfigurace: ").strip()
    if not name:
        print("❌ Název nesmí být prázdný")
        return
    
    # Kontrola, zda konfigurace již neexistuje
    configs = get_network_database_configs()
    if name in configs:
        overwrite = input(f"Konfigurace '{name}' již existuje. Přepsat? (y/N): ")
        if overwrite.lower() != 'y':
            return
    
    print("💡 Pro server 192.168.0.118 zadejte: 192.168.0.118")
    host = input("Server (IP adresa nebo hostname) [192.168.0.118]: ").strip()
    if not host:
        host = "192.168.0.118"
    
    try:
        port = int(input("Port (výchozí 5432): ") or "5432")
    except ValueError:
        print("❌ Port musí být číslo")
        return
    
    database = input("Název databáze (výchozí 'veterina'): ").strip() or "veterina"
    user = input("Uživatelské jméno (výchozí 'postgres'): ").strip() or "postgres"
    password = input("Heslo: ")
    
    config = {
        'host': host,
        'port': port,
        'database': database,
        'user': user,
        'password': password
    }
    
    # Test konfigurace
    print(f"\n🔍 Testování konfigurace '{name}'...")
    if test_database_connection(config):
        save_network_database_config(name, config)
        print(f"✅ Konfigurace '{name}' byla uložena")
        
        # Nabídka nastavení jako aktivní
        set_active = input("Nastavit jako aktivní konfiguraci? (Y/n): ")
        if set_active.lower() != 'n':
            set_active_network_config(name)
            print(f"✅ Konfigurace '{name}' je nyní aktivní")
    else:
        save_anyway = input("Připojení selhalo. Uložit konfiguraci přesto? (y/N): ")
        if save_anyway.lower() == 'y':
            save_network_database_config(name, config)
            print(f"⚠️ Konfigurace '{name}' byla uložena (bez testování)")

def test_configurations():
    """Testuje všechny konfigurace."""
    print("\n🔍 Testování všech konfigurací...")
    results = test_all_network_configs()
    
    print("\n📊 Výsledky:")
    working_configs = []
    for name, success in results.items():
        status = "✅ Funkční" if success else "❌ Nefunkční"
        print(f"  {name}: {status}")
        if success:
            working_configs.append(name)
    
    if working_configs:
        print(f"\n🎉 Funkční konfigurace: {', '.join(working_configs)}")
    else:
        print("\n⚠️ Žádná konfigurace není funkční")
        print("💡 Zkontrolujte:")
        print("   • Je PostgreSQL server na 192.168.0.118 spuštěn?")
        print("   • Je správně nakonfigurován firewall?")
        print("   • Máte správné přihlašovací údaje?")

def set_active_configuration():
    """Nastaví aktivní konfiguraci."""
    configs = get_network_database_configs()
    
    if not configs:
        print("❌ Žádné konfigurace nenalezeny")
        return
    
    print("\n📋 Dostupné konfigurace:")
    config_names = list(configs.keys())
    for i, name in enumerate(config_names, 1):
        config = configs[name]
        print(f"  {i}. {name} - {config['host']}:{config['port']}")
    
    try:
        choice = int(input("\nVyberte číslo konfigurace: ")) - 1
        if 0 <= choice < len(config_names):
            name = config_names[choice]
            if set_active_network_config(name):
                print(f"✅ Konfigurace '{name}' je nyní aktivní")
            else:
                print(f"❌ Chyba při nastavení konfigurace '{name}'")
        else:
            print("❌ Neplatné číslo")
    except ValueError:
        print("❌ Zadejte platné číslo")

def auto_detect_configuration():
    """Automaticky najde nejlepší konfiguraci."""
    print("\n🔍 Automatická detekce nejlepší konfigurace...")
    
    best_config = auto_detect_best_config()
    if best_config:
        set_active_network_config(best_config)
        print(f"✅ Automaticky nastavena konfigurace: {best_config}")
    else:
        print("❌ Žádná funkční konfigurace nenalezena")
        print("💡 Zkuste vytvořit výchozí konfigurace (volba 8)")

def show_current_connection():
    """Zobrazí informace o aktuálním připojení."""
    print(f"\n📡 Aktuální připojení: {get_connection_info()}")

def remove_configuration():
    """Odstraní konfiguraci."""
    configs = get_network_database_configs()
    
    if not configs:
        print("❌ Žádné konfigurace nenalezeny")
        return
    
    print("\n📋 Dostupné konfigurace:")
    config_names = list(configs.keys())
    for i, name in enumerate(config_names, 1):
        print(f"  {i}. {name}")
    
    try:
        choice = int(input("\nVyberte číslo konfigurace k odstranění: ")) - 1
        if 0 <= choice < len(config_names):
            name = config_names[choice]
            
            confirm = input(f"Opravdu odstranit konfiguraci '{name}'? (y/N): ")
            if confirm.lower() == 'y':
                # Odstraní konfiguraci z config.json
                from config import load_config, save_config
                config = load_config()
                if 'network_configs' in config and name in config['network_configs']:
                    del config['network_configs'][name]
                    
                    # Pokud byla aktivní, odstraní reference
                    if config.get('active_network_config') == name:
                        config['active_network_config'] = None
                    
                    save_config(config)
                    print(f"✅ Konfigurace '{name}' byla odstraněna")
                else:
                    print(f"❌ Konfigurace '{name}' nenalezena")
        else:
            print("❌ Neplatné číslo")
    except ValueError:
        print("❌ Zadejte platné číslo")

def create_default_configurations():
    """Vytvoří výchozí konfigurace."""
    print("\n🔧 Vytváření výchozích konfigurací...")
    create_default_configs()

def test_server_connection():
    """Test připojení k serveru 192.168.0.118."""
    print("\n🔍 Test připojení k serveru 192.168.0.118...")
    
    server_config = {
        'host': '192.168.0.118',
        'port': 5432,
        'database': 'veterina',
        'user': 'postgres',
        'password': input("Zadejte heslo pro postgres: ")
    }
    
    if test_database_connection(server_config):
        print("✅ Server 192.168.0.118 je dostupný!")
        save_choice = input("Uložit tuto konfiguraci jako 'server'? (Y/n): ")
        if save_choice.lower() != 'n':
            save_network_database_config('server', server_config)
            set_active_network_config('server')
            print("✅ Konfigurace 'server' byla uložena a nastavena jako aktivní")
    else:
        print("❌ Server 192.168.0.118 není dostupný")
        print("💡 Zkontrolujte síťové připojení a nastavení PostgreSQL serveru")

def main():
    """Hlavní funkce."""
    print("🌐 Network Database Configuration Manager")
    print("🗄️  PostgreSQL Server: 192.168.0.118")
    
    while True:
        show_menu()
        choice = input("Vyberte možnost: ").strip()
        
        if choice == '0':
            print("👋 Ukončuji...")
            break
        elif choice == '1':
            show_configurations()
        elif choice == '2':
            add_configuration()
        elif choice == '3':
            test_configurations()
        elif choice == '4':
            set_active_configuration()
        elif choice == '5':
            auto_detect_configuration()
        elif choice == '6':
            show_current_connection()
        elif choice == '7':
            remove_configuration()
        elif choice == '8':
            create_default_configurations()
        elif choice == '9':
            test_server_connection()
        else:
            print("❌ Neplatná volba")

if __name__ == "__main__":
    main()

import json
import os
import psycopg2
from typing import Dict, Any, Optional

CONFIG_FILE = "config.json"

def load_config():
    """Načte konfiguraci z config.json souboru."""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            pass
    return {}

def save_config(config):
    """Uloží konfiguraci do config.json souboru."""
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Nepodařilo se uložit konfiguraci: {e}")

# === POSTGRESQL KONFIGURACE ===

def get_database_config() -> Optional[Dict[str, Any]]:
    """Vrátí PostgreSQL databázovou konfiguraci."""
    config = load_config()
    return config.get('database_config')

def save_database_config(db_config: Dict[str, Any]):
    """Uloží PostgreSQL databázovou konfiguraci."""
    config = load_config()
    config['database_config'] = db_config
    config['database_type'] = 'postgresql'
    save_config(config)

def get_database_type() -> str:
    """Vrátí typ databáze - vždy postgresql."""
    return 'postgresql'

def set_database_type(db_type: str):
    """Nastaví typ databáze - pouze postgresql je povolený."""
    if db_type != 'postgresql':
        raise ValueError("Pouze PostgreSQL databáze je podporována!")
    config = load_config()
    config['database_type'] = 'postgresql'
    save_config(config)

# === SÍŤOVÁ KONFIGURACE ===

def get_network_database_configs() -> Dict[str, Dict[str, Any]]:
    """Vrátí uložené síťové konfigurace databází."""
    config = load_config()
    return config.get('network_configs', {})

def save_network_database_config(name: str, db_config: Dict[str, Any]):
    """Uloží pojmenovanou síťovou konfiguraci."""
    config = load_config()
    if 'network_configs' not in config:
        config['network_configs'] = {}
    config['network_configs'][name] = db_config
    save_config(config)

def set_active_network_config(name: str):
    """Nastaví aktivní síťovou konfiguraci."""
    network_configs = get_network_database_configs()
    if name in network_configs:
        save_database_config(network_configs[name])
        config = load_config()
        config['active_network_config'] = name
        save_config(config)
        return True
    return False

def get_active_network_config_name() -> Optional[str]:
    """Vrátí název aktivní síťové konfigurace."""
    config = load_config()
    return config.get('active_network_config')

# === TESTOVÁNÍ PŘIPOJENÍ ===

def test_database_connection(db_config: Optional[Dict[str, Any]] = None) -> bool:
    """Testuje připojení k PostgreSQL databázi."""
    if db_config is None:
        db_config = get_database_config()
    
    if not db_config:
        print("❌ Žádná databázová konfigurace nenalezena")
        return False
    
    try:
        print(f"🔍 Testování připojení k {db_config['host']}:{db_config['port']}")
        conn = psycopg2.connect(
            host=db_config['host'],
            port=db_config['port'],
            database=db_config['database'],
            user=db_config['user'],
            password=db_config['password'],
            connect_timeout=5
        )
        
        # Test základního dotazu
        cursor = conn.cursor()
        cursor.execute("SELECT version()")
        version = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        
        print(f"✅ Připojení úspěšné: {version[:50]}...")
        return True
        
    except psycopg2.OperationalError as e:
        error_msg = str(e)
        print(f"❌ Připojení selhalo: {error_msg}")
        
        if "could not connect to server" in error_msg:
            print("💡 Zkontrolujte:")
            print("   • Je PostgreSQL server spuštěn?")
            print("   • Je správně nakonfigurován firewall?")
            print("   • Je listen_addresses = '*' v postgresql.conf?")
        elif "authentication failed" in error_msg:
            print("💡 Zkontrolujte uživatelské jméno a heslo")
        elif "database" in error_msg and "does not exist" in error_msg:
            print(f"💡 Databáze '{db_config['database']}' neexistuje")
        
        return False
    except Exception as e:
        print(f"❌ Neočekávaná chyba: {e}")
        return False

def test_all_network_configs() -> Dict[str, bool]:
    """Testuje všechny uložené síťové konfigurace."""
    network_configs = get_network_database_configs()
    results = {}
    
    print("=== TESTOVÁNÍ VŠECH SÍŤOVÝCH KONFIGURACÍ ===")
    
    for name, config in network_configs.items():
        print(f"\n🔍 Testování konfigurace '{name}':")
        results[name] = test_database_connection(config)
    
    return results

def get_best_database_config():
    """Vrátí nejlepší dostupnou PostgreSQL databázovou konfiguraci."""
    # Zkusíme aktuální konfiguraci
    current_config = get_database_config()
    if current_config and test_database_connection(current_config):
        return current_config, "current"
    
    # Zkusíme síťové konfigurace
    network_configs = get_network_database_configs()
    for name, config in network_configs.items():
        if test_database_connection(config):
            print(f"✅ Používám konfiguraci '{name}'")
            return config, name
    
    # Pokud nic nefunguje, vyhodíme chybu
    if current_config:
        raise Exception(f"PostgreSQL databáze není dostupná na {current_config['host']}!")
    else:
        raise Exception("Žádná PostgreSQL konfigurace není dostupná!")

def auto_detect_best_config() -> Optional[str]:
    """Automaticky detekuje nejlepší dostupnou konfiguraci."""
    network_configs = get_network_database_configs()
    
    # Nejdříve zkusíme localhost
    if 'localhost' in network_configs:
        if test_database_connection(network_configs['localhost']):
            print("✅ Localhost PostgreSQL je dostupný")
            return 'localhost'
    
    # Pak zkusíme server
    if 'server' in network_configs:
        if test_database_connection(network_configs['server']):
            print("✅ Síťový server PostgreSQL je dostupný")
            return 'server'
    
    # Zkusíme ostatní konfigurace
    for name, config in network_configs.items():
        if name not in ['localhost', 'server']:
            if test_database_connection(config):
                print(f"✅ Konfigurace '{name}' je dostupná")
                return name
    
    return None

# === UTILITY FUNKCE ===

def create_default_configs():
    """Vytvoří výchozí síťové konfigurace s IP 192.168.0.118."""
    default_configs = {
        'localhost': {
            'host': 'localhost',
            'port': 5432,
            'database': 'veterina',
            'user': 'postgres',
            'password': 'motodevka25'
        },
        'server': {
            'host': '192.168.0.118',
            'port': 5432,
            'database': 'veterina',
            'user': 'postgres',
            'password': 'motodevka25'
        }
    }
    
    for name, config in default_configs.items():
        save_network_database_config(name, config)
    
    print("✅ Výchozí síťové konfigurace vytvořeny pro server 192.168.0.118")

def ensure_database_config():
    """Zajistí, že existuje PostgreSQL databázová konfigurace."""
    db_config = get_database_config()
    
    if not db_config:
        print("⚠️ Žádná databázová konfigurace nenalezena")
        
        # Vytvoří výchozí konfigurace pokud neexistují
        network_configs = get_network_database_configs()
        if not network_configs:
            create_default_configs()
        
        # Pokusí se najít funkční konfiguraci
        best_config = auto_detect_best_config()
        if best_config:
            set_active_network_config(best_config)
            return get_database_config()
        else:
            # Fallback na server 192.168.0.118
            default_config = {
                "host": "192.168.0.118",
                "port": 5432,
                "database": "veterina",
                "user": "postgres",
                "password": "motodevka25"
            }
            print("📝 Nastavujem výchozí konfiguraci pro server 192.168.0.118")
            save_database_config(default_config)
            return default_config
    
    return db_config

def get_connection_info() -> str:
    """Vrátí informace o připojení k PostgreSQL databázi."""
    config = get_database_config()
    if config:
        active_name = get_active_network_config_name()
        prefix = f"[{active_name}] " if active_name else ""
        return f"{prefix}PostgreSQL: {config['user']}@{config['host']}:{config['port']}/{config['database']}"
    return "PostgreSQL: Není nakonfigurováno"

# === ZPĚTNÁ KOMPATIBILITA ===

def get_last_directory():
    """Vrátí poslední použitou složku."""
    config = load_config()
    return config.get('last_directory', os.path.expanduser('~'))

def get_database_path_from_config():
    """Vrátí cestu k databázi z konfigurace (pro SQLite) - deprecated."""
    config = load_config()
    return config.get('database_path', '')

def save_database_path_to_config(path):
    """Uloží cestu k databázi do konfigurace (pro SQLite) - deprecated."""
    config = load_config()
    config['database_path'] = path
    config['database_type'] = 'sqlite'
    config['last_directory'] = os.path.dirname(path)
    save_config(config)

# === INICIALIZACE ===

def initialize_config():
    """Inicializuje PostgreSQL konfiguraci při prvním spuštění."""
    if not os.path.exists(CONFIG_FILE):
        print("📝 Vytvářím nový konfigurační soubor pro PostgreSQL...")
        
        # Výchozí konfigurace s IP 192.168.0.118
        default_config = {
            "database_type": "postgresql",
            "database_config": {
                "host": "192.168.0.118",
                "port": 5432,
                "database": "veterina",
                "user": "postgres",
                "password": "motodevka25"
            },
            "network_configs": {
                "localhost": {
                    "host": "localhost",
                    "port": 5432,
                    "database": "veterina",
                    "user": "postgres",
                    "password": "motodevka25"
                },
                "server": {
                    "host": "192.168.0.118",
                    "port": 5432,
                    "database": "veterina",
                    "user": "postgres",
                    "password": "motodevka25"
                }
            },
            "active_network_config": "server"
        }
        save_config(default_config)
        print("✅ PostgreSQL konfigurační soubor vytvořen s IP 192.168.0.118")

# Spustí se při importu - vždy PostgreSQL
if not os.path.exists(CONFIG_FILE):
    initialize_config()

import json
import os
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
    config['database_type'] = 'postgresql'  # Označí typ databáze
    save_config(config)

def get_database_type() -> str:
    """Vrátí typ databáze (postgresql/sqlite)."""
    config = load_config()
    return config.get('database_type', 'sqlite')  # Výchozí pro zpětnou kompatibilitu

def set_database_type(db_type: str):
    """Nastaví typ databáze."""
    config = load_config()
    config['database_type'] = db_type
    save_config(config)

# === ZPĚTNÁ KOMPATIBILITA PRO SQLITE ===

def get_database_path_from_config():
    """Vrátí cestu k databázi z konfigurace (pro SQLite)."""
    config = load_config()
    return config.get('database_path', '')

def save_database_path_to_config(path):
    """Uloží cestu k databázi do konfigurace (pro SQLite)."""
    config = load_config()
    config['database_path'] = path
    config['database_type'] = 'sqlite'
    # Uložíme také složku pro usnadnění dalšího použití
    config['last_directory'] = os.path.dirname(path)
    save_config(config)

def get_last_directory():
    """Vrátí poslední použitou složku."""
    config = load_config()
    return config.get('last_directory', os.path.expanduser('~'))

# === POMOCNÉ FUNKCE ===

def ensure_database_config():
    """Zajistí, že existuje databázová konfigurace."""
    db_type = get_database_type()
    
    if db_type == 'postgresql':
        db_config = get_database_config()
        if not db_config:
            # Výchozí PostgreSQL konfigurace
            default_config = {
                "host": "192.168.0.118",
                "port": 5432,
                "database": "veterina",
                "user": "postgres",
                "password": "motodevka25"
            }
            print("Vytvářím výchozí PostgreSQL konfiguraci...")
            save_database_config(default_config)
            return default_config
        return db_config
    else:
        # SQLite - vrátí cestu
        return get_database_path_from_config()

def test_database_connection() -> bool:
    """Testuje připojení k databázi podle typu."""
    db_type = get_database_type()
    
    if db_type == 'postgresql':
        try:
            import psycopg2
            config = get_database_config()
            if not config:
                return False
            
            conn = psycopg2.connect(**config)
            conn.close()
            return True
        except Exception:
            return False
    else:
        # SQLite test
        import sqlite3
        import os
        path = get_database_path_from_config()
        return path and os.path.exists(path)

def get_connection_info() -> str:
    """Vrátí informace o připojení k databázi."""
    db_type = get_database_type()
    
    if db_type == 'postgresql':
        config = get_database_config()
        if config:
            return f"PostgreSQL: {config['user']}@{config['host']}:{config['port']}/{config['database']}"
        return "PostgreSQL: Není nakonfigurováno"
    else:
        path = get_database_path_from_config()
        return f"SQLite: {path}" if path else "SQLite: Není nakonfigurováno"

# === INICIALIZACE ===

def initialize_config():
    """Inicializuje konfiguraci při prvním spuštění."""
    if not os.path.exists(CONFIG_FILE):
        print("Vytvářím nový konfigurační soubor...")
        # Výchozí konfigurace
        default_config = {
            "database_type": "postgresql",  # Defaultně PostgreSQL
            "database_config": {
                "host": "localhost",
                "port": 5432,
                "database": "veterina",
                "user": "postgres",
                "password": "motodevka25"
            },
            "last_directory": os.path.expanduser('~')
        }
        save_config(default_config)
        print("✅ Konfigurační soubor vytvořen")

# Spustí se při importu
if not os.path.exists(CONFIG_FILE):
    initialize_config()

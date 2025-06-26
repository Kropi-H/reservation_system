import json
import os

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

def get_database_path_from_config():
    """Vrátí cestu k databázi z konfigurace."""
    config = load_config()
    return config.get('database_path', '')

def save_database_path_to_config(path):
    """Uloží cestu k databázi do konfigurace."""
    config = load_config()
    config['database_path'] = path
    # Uložíme také složku pro usnadnění dalšího použití
    config['last_directory'] = os.path.dirname(path)
    save_config(config)

def get_last_directory():
    """Vrátí poslední použitou složku."""
    config = load_config()
    return config.get('last_directory', os.path.expanduser('~'))

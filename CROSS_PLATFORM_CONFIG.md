# ⚙️ CROSS-PLATFORM CONFIG - Cesty a nastavení aplikace

## 📋 Přehled

Tento návod pokrývá správu konfiguračních souborů napříč platformami a specifické nastavení pro každý OS.

| Platform | Config adresář | Přístup | Status |
|----------|----------------|---------|--------|
| **Windows** | `%LOCALAPPDATA%\ReservationSystem\` | User-specific | ✅ |
| **Linux** | `~/.config/ReservationSystem/` | User-specific | ✅ |
| **macOS** | `~/Library/Application Support/ReservationSystem/` | User-specific | ✅ |

---

## 📁 AUTOMATICKÁ DETEKCE KONFIGURACE

### 🎯 Python kód pro detekci OS
```python
import sys
import os

def get_config_path():
    """Automaticky detekuje správnou cestu pro konfiguraci podle OS."""
    if sys.platform == "win32":
        # Windows
        config_dir = os.path.join(os.environ['LOCALAPPDATA'], 'ReservationSystem')
    elif sys.platform == "darwin":
        # macOS
        config_dir = os.path.expanduser('~/Library/Application Support/ReservationSystem')
    else:
        # Linux a ostatní Unix systémy
        config_dir = os.path.expanduser('~/.config/ReservationSystem')
    
    # Vytvoř adresář pokud neexistuje
    os.makedirs(config_dir, exist_ok=True)
    return config_dir

def get_config_file_path():
    """Vrátí cestu k hlavnímu config souboru."""
    return os.path.join(get_config_path(), 'config.json')

def get_chat_config_file_path():
    """Vrátí cestu k chat config souboru."""
    return os.path.join(get_config_path(), 'chat_config.json')
```

### 🔄 Migrace ze starých umístění
```python
def migrate_old_config():
    """Migruje konfiguraci ze starého umístění (kořen projektu) na nové."""
    old_config = "config.json"
    old_chat_config = "chat_config.json"
    
    new_config = get_config_file_path()
    new_chat_config = get_chat_config_file_path()
    
    # Migrace hlavní konfigurace
    if os.path.exists(old_config) and not os.path.exists(new_config):
        import shutil
        shutil.copy2(old_config, new_config)
        print(f"✅ Konfigurace migrována: {old_config} → {new_config}")
    
    # Migrace chat konfigurace
    if os.path.exists(old_chat_config) and not os.path.exists(new_chat_config):
        import shutil
        shutil.copy2(old_chat_config, new_chat_config)
        print(f"✅ Chat konfigurace migrována: {old_chat_config} → {new_chat_config}")
```

---

## 🖥️ WINDOWS KONFIGURACE

### 📂 Umístění souborů
```
%LOCALAPPDATA%\ReservationSystem\
├── config.json          # Hlavní databázová konfigurace
└── chat_config.json     # Chat nastavení
```

**Plná cesta:** `C:\Users\[username]\AppData\Local\ReservationSystem\`

### 🔍 Zjištění cesty ve Windows
```powershell
# PowerShell
echo $env:LOCALAPPDATA\ReservationSystem

# CMD
echo %LOCALAPPDATA%\ReservationSystem

# Přímá navigace
explorer %LOCALAPPDATA%\ReservationSystem
```

### 📝 Struktura config.json (Windows)
```json
{
    "host": "192.168.0.118",
    "port": 5432,
    "database": "veterina_db",
    "username": "postgres",
    "password": "tvoje_heslo",
    "last_updated": "2025-09-02T16:30:00"
}
```

### 💬 Struktura chat_config.json (Windows)
```json
{
    "mode": "client",
    "server_ip": "192.168.0.118",
    "server_port": 12345,
    "auto_connect": true,
    "last_updated": "2025-09-02T16:30:00"
}
```

### 🔧 Windows PowerShell správa
```powershell
# Zobraz config
Get-Content "$env:LOCALAPPDATA\ReservationSystem\config.json" | ConvertFrom-Json | Format-List

# Vytvoř zálohu
Copy-Item "$env:LOCALAPPDATA\ReservationSystem\*" -Destination ".\backup\" -Recurse

# Smaž konfiguraci (reset)
Remove-Item "$env:LOCALAPPDATA\ReservationSystem\" -Recurse -Force
```

---

## 🐧 LINUX KONFIGURACE

### 📂 Umístění souborů
```
~/.config/ReservationSystem/
├── config.json          # Hlavní databázová konfigurace
└── chat_config.json     # Chat nastavení
```

**Plná cesta:** `/home/[username]/.config/ReservationSystem/`

### 🔍 Zjištění cesty v Linuxu
```bash
# Bash
echo ~/.config/ReservationSystem

# Navigace
cd ~/.config/ReservationSystem
ls -la

# Otevři v file manageru (Ubuntu)
nautilus ~/.config/ReservationSystem
```

### 📝 Struktura config.json (Linux)
```json
{
    "host": "192.168.0.118",
    "port": 5432,
    "database": "veterina_db",
    "username": "postgres",
    "password": "tvoje_heslo",
    "last_updated": "2025-09-02T16:30:00"
}
```

### 🔧 Linux bash správa
```bash
# Zobraz config
cat ~/.config/ReservationSystem/config.json | jq .

# Vytvoř zálohu
cp -r ~/.config/ReservationSystem ~/reservation_backup_$(date +%Y%m%d)

# Smaž konfiguraci (reset)
rm -rf ~/.config/ReservationSystem

# Oprávnění (pokud potřeba)
chmod 600 ~/.config/ReservationSystem/*.json
```

---

## 🍎 macOS KONFIGURACE

### 📂 Umístění souborů
```
~/Library/Application Support/ReservationSystem/
├── config.json          # Hlavní databázová konfigurace
└── chat_config.json     # Chat nastavení
```

**Plná cesta:** `/Users/[username]/Library/Application Support/ReservationSystem/`

### 🔍 Zjištění cesty v macOS
```bash
# Terminal
echo "~/Library/Application Support/ReservationSystem"

# Navigace
cd "~/Library/Application Support/ReservationSystem"
ls -la

# Otevři v Finderu
open "~/Library/Application Support/ReservationSystem"
```

### 🔧 macOS Terminal správa
```bash
# Zobraz config
cat "~/Library/Application Support/ReservationSystem/config.json" | jq .

# Vytvoř zálohu
cp -r "~/Library/Application Support/ReservationSystem" ~/Desktop/reservation_backup_$(date +%Y%m%d)

# Smaž konfiguraci (reset)
rm -rf "~/Library/Application Support/ReservationSystem"
```

---

## 🐘 POSTGRESQL SETUP NA WINDOWS

### 📥 Instalace PostgreSQL
```powershell
# Možnost 1: Stáhni z webu
# https://www.postgresql.org/download/windows/

# Možnost 2: Chocolatey
choco install postgresql

# Možnost 3: Winget
winget install PostgreSQL.PostgreSQL

# Možnost 4: Scoop
scoop install postgresql
```

### ⚙️ Základní konfigurace PostgreSQL
```powershell
# Po instalaci - nastavení hesla
# Spustí se automaticky setup wizard

# Nebo manuálně přes psql
psql -U postgres

# Vytvoř databázi
CREATE DATABASE veterina_db;
CREATE USER veterina_user WITH PASSWORD 'silne_heslo';
GRANT ALL PRIVILEGES ON DATABASE veterina_db TO veterina_user;
```

### 🔥 Konfigurace Windows Firewall
```powershell
# Otevři PowerShell jako Administrator

# Povolit PostgreSQL port (5432)
New-NetFirewallRule -DisplayName "PostgreSQL" -Direction Inbound -Port 5432 -Protocol TCP -Action Allow

# Nebo přes netsh
netsh advfirewall firewall add rule name="PostgreSQL" dir=in action=allow protocol=TCP localport=5432

# Ověření pravidla
Get-NetFirewallRule -DisplayName "PostgreSQL"
```

### 🌐 Povolení vzdálených připojení
```powershell
# Najdi PostgreSQL konfigurace
# Obvykle: C:\Program Files\PostgreSQL\15\data\

# Edituj postgresql.conf
# listen_addresses = '*'          # nebo specific IP
# port = 5432

# Edituj pg_hba.conf (přidej na konec)
# host    all             all             192.168.0.0/24          md5
# host    all             all             0.0.0.0/0               md5   # POZOR: Nebezpečné pro produkci!

# Restartuj PostgreSQL službu
Restart-Service postgresql-x64-15
```

### 🔍 Windows PostgreSQL troubleshooting
```powershell
# Zkontroluj službu
Get-Service postgresql*

# Zkontroluj port
netstat -an | findstr :5432

# Zkontroluj logy
Get-Content "C:\Program Files\PostgreSQL\15\data\log\*.log" -Tail 50

# Test připojení
psql -h localhost -U postgres -d veterina_db
```

### 🏠 Lokální vs. síťové nastavení
```json
// Lokální připojení (pouze tento PC)
{
    "host": "localhost",
    "port": 5432,
    "database": "veterina_db",
    "username": "postgres",
    "password": "tvoje_heslo"
}

// Síťové připojení (více PC)
{
    "host": "192.168.0.118",
    "port": 5432,
    "database": "veterina_db", 
    "username": "postgres",
    "password": "tvoje_heslo"
}
```

---

## 🔒 BEZPEČNOST KONFIGURACE

### 🛡️ Oprávnění souborů

#### Windows:
```powershell
# Nastav oprávnění pouze pro aktuálního uživatele
icacls "%LOCALAPPDATA%\ReservationSystem\config.json" /inheritance:r /grant:r "%USERNAME%:F"
```

#### Linux/macOS:
```bash
# Nastav oprávnění pouze pro vlastníka
chmod 600 ~/.config/ReservationSystem/*.json
```

### 🔐 Šifrování citlivých dat
```python
import base64
from cryptography.fernet import Fernet

def encrypt_password(password, key):
    """Zašifruj heslo."""
    f = Fernet(key)
    encrypted = f.encrypt(password.encode())
    return base64.b64encode(encrypted).decode()

def decrypt_password(encrypted_password, key):
    """Dešifruj heslo."""
    f = Fernet(key)
    encrypted = base64.b64decode(encrypted_password.encode())
    return f.decrypt(encrypted).decode()

# Použití:
# key = Fernet.generate_key()  # Ulož bezpečně
# encrypted = encrypt_password("moje_heslo", key)
```

---

## 🔄 SYNCHRONIZACE KONFIGURACE

### 📱 Pro více zařízení
```python
def sync_config_from_server(server_config_url):
    """Stáhni konfiguraci ze serveru."""
    import requests
    response = requests.get(server_config_url)
    if response.status_code == 200:
        config = response.json()
        save_config(config)
        return True
    return False

def backup_config_to_server(server_backup_url):
    """Zálohuj konfiguraci na server."""
    import requests
    config = load_config()
    response = requests.post(server_backup_url, json=config)
    return response.status_code == 200
```

---

## ✅ CHECKLIST KONFIGURACE

### Před distribucí:
- [ ] Cross-platform detekce implementována
- [ ] Migrace ze starých umístění funkční
- [ ] Konfigurace se ukládá na správná místa
- [ ] Oprávnění souborů nastavena

### PostgreSQL na Windows:
- [ ] PostgreSQL nainstalován
- [ ] Databáze vytvořena
- [ ] Firewall nakonfigurován
- [ ] Vzdálená připojení povolena (pokud potřeba)
- [ ] Připojení otestováno

### Bezpečnost:
- [ ] Hesla nejsou v plain textu (doporučeno)
- [ ] Oprávnění souborů omezena
- [ ] Backup strategie nastavena

---

**Vytvořeno:** 2.9.2025  
**Status:** 🟢 Ready for multi-platform deployment

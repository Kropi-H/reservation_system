# 🍎 Spuštění aplikace na macOS - AKTUALIZOVÁNO

## � Nejnovější opravy
- ✅ Přidán správný název aplikace (`setApplicationName`)
- ✅ Opravena struktura macOS menu
- ✅ Přidána Quit akce s Cmd+Q
- ✅ Vytvořen test script pro ověření menu

## 🚀 Rychlé spuštění

### 1. Otevřete Terminal
```bash
# Přejděte do složky projektu
cd /path/to/reservation_system

# Spusťte aplikaci
python3 main.py
```

### 2. Po spuštění hledejte menu:
**V horní liště systému** by se mělo objevit menu **"ReservationSystem"** (ne "Python"!)

## 🧪 Test menu funkcionalnosti

Pokud stále vidíte jen "Python" menu, zkuste nejprve test:

```bash
python3 test_macos_menu.py
```

Tento test by měl ukázat menu "TestApp" v horní liště. Pokud funguje, pak víme, že problém je v hlavní aplikaci.

## 🐛 Řešení problému s "Python" menu

### Problém: 
V horní liště vidíte jen "Python" s možnostmi "Services, Hide main.py, Hide Others, Quit main.py"

### Řešení:
1. **Ukončete aplikaci** (Cmd+Q nebo zavřít okno)
2. **Spusťte znovu**: `python3 main.py`
3. **Sledujte konzoli** pro zprávy:
   - `🍎 Konfiguruji menu pro macOS...`
   - `🍎 macOS menu struktura vytvořena - hledejte 'ReservationSystem' v horní liště`

### Co by se mělo stát:
- V horní liště se objeví **"ReservationSystem"** (místo "Python")
- Po kliknutí na něj uvidíte:
  - ✅ "Přihlášení"
  - ✅ "Ukončit ReservationSystem"

## 🔍 Debug kroky

### 1. Zkontrolujte debug výstup:
```bash
python3 main.py | grep "🍎"
```

### 2. Pokud nevidíte 🍎 zprávy:
```bash
python3 -c "import platform; print(f'OS: {platform.system()}')"
```
Mělo by ukázat: `OS: Darwin`

### 3. Test jednoduchého menu:
```bash
python3 test_macos_menu.py
```

## ⚡ Rychlé řešení

Pokud nic nefunguje:

1. **Restartujte Terminal**
2. **Ujistěte se, že jste ve správné složce**:
   ```bash
   ls -la | grep main.py
   ```
3. **Spusťte s verbose výstupem**:
   ```bash
   python3 main.py 2>&1 | head -20
   ```

## 📞 Pokud stále problém

Sdílejte prosím:
1. Výstup z `python3 main.py | head -10`
2. Výstup z `python3 test_macos_menu.py`
3. Screenshot horní lišty s menu

---

**Klíčová změna**: Aplikace by se teď měla jmenovat "ReservationSystem" v menu, ne "Python"!

## 🔧 Alternativní způsoby spuštění

### Způsob 1: Přímé spuštění
```bash
python3 main.py
```

### Způsob 2: S modulem
```bash
python3 -m main
```

### Způsob 3: Spustitelný soubor
```bash
# Pokud je main.py označen jako spustitelný
chmod +x main.py
./main.py
```

## 🐛 Řešení problémů

### Python není nalezen
```bash
# Zkuste tyto varianty:
python main.py
python3 main.py
/usr/bin/python3 main.py

# Nebo nainstalujte Python přes Homebrew:
brew install python
```

### Chybějící závislosti
```bash
# Instalace konkrétních balíčků:
pip3 install PySide6
pip3 install psycopg2-binary
pip3 install requests

# Nebo celý requirements.txt:
pip3 install -r requirements.txt
```

### Problém s PostgreSQL
```bash
# Instalace PostgreSQL na macOS:
brew install postgresql
brew services start postgresql

# Nebo použijte SQLite (výchozí):
# Aplikace automaticky vytvoří SQLite databázi
```

### Oprávnění
```bash
# Pokud máte problém s oprávněními:
chmod +x main.py
chmod -R 755 .
```

## 🍎 Specifika pro macOS

### Menu Bar
- **DŮLEŽITÉ**: Menu se zobrazí v horní liště systému, ne v okně aplikace
- Hledejte "ReservationSystem" vedle Apple logo
- Klikněte tam pro přihlášení

### Bezpečnost
- macOS může zobrazit varování o neověřené aplikaci
- Klikněte "Otevřít přesto" v System Preferences > Security & Privacy

### Ikony a obrázky
- Aplikace automaticky najde ikony ve složce `pictures/`
- Logo se zobrazí v hlavním okně

## 📝 Debug režim
Pro sledování problémů spusťte s debug výstupem:

```bash
python3 main.py 2>&1 | grep -E "🍎|ERROR|Exception"
```

## 🔍 Kontrolní seznam
- [ ] Python 3.8+ nainstalován
- [ ] Všechny závislosti nainstalovány
- [ ] V správné složce projektu
- [ ] Terminal spuštěn
- [ ] Příkaz `python3 main.py` spuštěn
- [ ] Menu hledáte v horní liště systému

## 📞 Pokud stále nefunguje
1. Zkopírujte celý error výstup
2. Spusťte: `python3 --version && pip3 list | grep -E "PySide6|psycopg2"`
3. Sdílte výsledky pro další pomoc

---

**Tip**: Na macOS je nejjednodušší způsob `python3 main.py` z Terminálu ve správné složce.

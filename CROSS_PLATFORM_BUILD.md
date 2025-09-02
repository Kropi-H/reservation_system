# 🏗️ CROSS-PLATFORM BUILD - Návod na vytváření spouštěcích souborů

> ⚠️ **Důležité:** GitHub Actions buildy jsou dočasně vypnuté kvůli problémům s logy. Používej lokální build!

## 📋 Rychlé odkazy
- 🪟 **Windows**: Lokální build (návod níže) - ✅ **DOPORUČENO**
- 🍎 **macOS**: [build_macos.sh](build_macos.sh) nebo [MACOS_INSTALLATION.md](MACOS_INSTALLATION.md)
- 🐧 **Linux**: [build_linux.sh](build_linux.sh) 
- 🤖 **GitHub Actions**: Dočasně vypnuté

## 🎯 Unified Build System (Lokální)
```powershell
# POZNÁMKA: Virtuální prostředí s "python -m venv venv" může NEFUNGOVAT
# na některých systémech. Doporučuje se použít plnou cestu k Pythonu:

# Pokročilý build (nejspolehlivější):
& "C:/Program Files/Python38/python.exe" -m PyInstaller --onefile --noconsole --name "ReservationSystem" --icon="pictures\karakal_logo_grey.ico" --add-data="assets;assets" --add-data="pictures;pictures" main.py

# Pokud chybí moduly, přidej:
& "C:/Program Files/Python38/python.exe" -m PyInstaller --onefile --noconsole ^
    --hidden-import=PySide6.QtWidgets ^
    --hidden-import=psycopg2 ^
    --hidden-import=sys ^
    --hidden-import=os ^
    --hidden-import=json ^
    --name "ReservationSystem" main.py

# Pokud antivirus blokuje
# 1. Přidej dist\ složku do výjimek
# 2. Nebo dočasně vypni real-time protection

# Pokud je .exe příliš pomalý při startu
# Normal - první spuštění trvá 5-10 sekund
# Další spuštění jsou rychlejší
``` Přehled

Tento návod pokrývá vytvoření standalone spouštěcích souborů pro všechny hlavní platformy.

| Platform | Výstup | Velikost | Testováno |
|----------|--------|----------|-----------|
| **Windows** | `.exe` | ~45MB | ✅ |
| **Linux** | `binary` / `.AppImage` | ~40MB | ⚠️ |
| **macOS** | `.app` / `.dmg` | ~50MB | ⚠️ |

---

## 🖥️ WINDOWS BUILD

### 🔧 Předpoklady
```powershell
# Ověř Python verzi (3.8+ doporučeno)
python --version

# Ověř že aplikace funguje
python main.py

# Nainstaluj PyInstaller
pip install pyinstaller

# Ověř PyInstaller
pyinstaller --version
```

### 🚀 Základní build
```powershell
# Přejdi do projektové složky
cd "C:\Users\kropa\PycharmProjects\reservation_system"

# Základní .exe (bez ikon)
& "C:/Program Files/Python38/python.exe" -m PyInstaller --onefile --noconsole --name "ReservationSystem" main.py
```

**Výsledek:** `dist\ReservationSystem.exe` (~45MB)

### 🎯 Pokročilý build (s ikonami a resources) - DOPORUČENO
```powershell
# Kompletní build s ikonou a soubory (jako včera)
& "C:/Program Files/Python38/python.exe" -m PyInstaller --onefile --noconsole --name "ReservationSystem" --icon="pictures\karakal_logo_grey.ico" --add-data="assets;assets" --add-data="pictures;pictures" main.py
```

### 🧪 Test Windows .exe
```powershell
# Spusť .exe
.\dist\ReservationSystem.exe

# Zkopíruj na jiný počítač bez Pythonu
# Ověř všechny funkce (DB, chat, rezervace)
```

### ⚠️ Řešení problémů Windows
```powershell
# Pokud chybí moduly
pyinstaller --onefile --noconsole ^
    --hidden-import=sys ^
    --hidden-import=os ^
    --hidden-import=json ^
    --hidden-import=socket ^
    --hidden-import=threading ^
    --name "ReservationSystem" main.py

# Pokud antivirus blokuje
# 1. Přidej dist\ složku do výjimek
# 2. Nebo dočasně vypni real-time protection

# Pokud je .exe příliš pomalý při startu
# Normal - první spuštění trvá 5-10 sekund
# Další spuštění jsou rychlejší
```

---

## 🐧 LINUX BUILD

### 🔧 Předpoklady Ubuntu/Debian
```bash
# Aktualizuj systém
sudo apt update && sudo apt upgrade -y

# Nainstaluj Python a pip
sudo apt install python3 python3-pip python3-venv -y

# Vytvoř virtuální prostředí
python3 -m venv venv
source venv/bin/activate

# Nainstaluj závislosti
pip install -r requirements.txt
pip install pyinstaller
```

### 🚀 Základní Linux binary
```bash
# Přejdi do projektové složky
cd "/home/$(whoami)/reservation_system"

# Vytvoř Linux binary (ikona se nastavuje přes .desktop soubor)
pyinstaller --onefile --name "ReservationSystem" --add-data="assets:assets" --add-data="pictures:pictures" main.py

# Vytvoř .desktop soubor pro ikonu
cat > ReservationSystem.desktop << EOF
[Desktop Entry]
Type=Application
Name=Reservation System
Comment=Veterinary Reservation System
Exec=$(pwd)/dist/ReservationSystem
Icon=$(pwd)/pictures/karakal_logo_grey.png
Categories=Office;Database;
Terminal=false
EOF

# Nainstaluj ikonu do systému (optional)
desktop-file-install --dir=~/.local/share/applications ReservationSystem.desktop
```

**Výsledek:** `dist/ReservationSystem` (~40MB)

**Poznámka:** Na Linuxu PyInstaller nepodporuje `--icon` parametr. Ikona se nastavuje přes .desktop soubor.

### 📦 AppImage (doporučeno pro distribuci)
```bash
# Stáhni AppImageTool
wget https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage
chmod +x appimagetool-x86_64.AppImage

# Vytvoř AppDir strukturu
mkdir -p ReservationSystem.AppDir/usr/bin
mkdir -p ReservationSystem.AppDir/usr/share/applications
mkdir -p ReservationSystem.AppDir/usr/share/icons/hicolor/256x256/apps

# Zkopíruj binary
cp dist/ReservationSystem ReservationSystem.AppDir/usr/bin/

# Zkopíruj ikonu (pokud existuje PNG verze)
cp pictures/karakal_logo_grey.png ReservationSystem.AppDir/usr/share/icons/hicolor/256x256/apps/ReservationSystem.png

# Vytvoř .desktop soubor
cat > ReservationSystem.AppDir/ReservationSystem.desktop << 'EOF'
[Desktop Entry]
Type=Application
Name=Reservation System
Exec=ReservationSystem
Icon=ReservationSystem
Categories=Office;Database;
Comment=Veterinary Reservation System
EOF

# Vytvoř AppRun script
cat > ReservationSystem.AppDir/AppRun << 'EOF'
#!/bin/bash
SELF=$(readlink -f "$0")
HERE=${SELF%/*}
exec "${HERE}/usr/bin/ReservationSystem" "$@"
EOF
chmod +x ReservationSystem.AppDir/AppRun

# Vytvoř AppImage
./appimagetool-x86_64.AppImage ReservationSystem.AppDir ReservationSystem-x86_64.AppImage
```

**Výsledek:** `ReservationSystem-x86_64.AppImage` (~40MB)

### 🧪 Test Linux binary
```bash
# Test základní binary
./dist/ReservationSystem

# Test AppImage
chmod +x ReservationSystem-x86_64.AppImage
./ReservationSystem-x86_64.AppImage

# Install AppImage (optional)
mkdir -p ~/.local/bin
cp ReservationSystem-x86_64.AppImage ~/.local/bin/
```

### ⚠️ Řešení problémů Linux
```bash
# ❌ GLIBC chyba: "GLIBC_2.38 not found"
# Problém: GitHub Actions Ubuntu má novější GLIBC než váš Linux Mint

# ŘEŠENÍ 1: Použij Python variantu (nejspolehlivější)
git clone https://github.com/Kropi-H/reservation_system.git
cd reservation_system
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py

# ŘEŠENÍ 2: Stáhni AppImage místo binary
# AppImage má lepší kompatibilitu napříč distribucemi
chmod +x ReservationSystem-x86_64.AppImage
./ReservationSystem-x86_64.AppImage

# Pokud chybí Qt knihovny (druhý nejčastější problém)
sudo apt update
sudo apt install -y libxcb-xinerama0 libxcb1 libx11-6 libxrandr2 libxss1 libxcursor1 libxdamage1 libxfixes3 libxcomposite1 libxi6 libxtst6 libgl1-mesa-glx

# Pokud chybí audio knihovny (pro Qt)
sudo apt install -y libasound2 libpulse0

# Pokud nefunguje systémová integrace
sudo apt install -y libfuse2

# Pro Linux Mint specificky:
sudo apt install -y libglib2.0-0 libfontconfig1 libxrender1 libnss3 libatk-bridge2.0-0 libdrm2 libgbm1

# Spuštění s debug informacemi:
QT_DEBUG_PLUGINS=1 ./ReservationSystem

# Diagnóza chybějících knihoven:
ldd ReservationSystem | grep "not found"

# Zkontroluj GLIBC verzi:
ldd --version

# Správná oprávnění (ne 777!):
chmod +x ReservationSystem
```

---

## 🍎 macOS BUILD

### 🔧 Předpoklady macOS
```bash
# Nainstaluj Homebrew (pokud nemáš)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Nainstaluj Python
brew install python

# Vytvoř virtuální prostředí
python3 -m venv venv
source venv/bin/activate

# Nainstaluj závislosti
pip install -r requirements.txt
pip install pyinstaller
```

### 🚀 Základní .app bundle
```bash
# Přejdi do projektové složky
cd "/Users/$(whoami)/reservation_system"

# Vytvoř .app bundle
pyinstaller --onefile --windowed --name "ReservationSystem" main.py
```

**Výsledek:** `dist/ReservationSystem.app` (~50MB)

### 🎯 Pokročilý .app s ikonou
```bash
# Pokud máš .icns ikonu
pyinstaller --onefile --windowed \
    --name "ReservationSystem" \
    --icon="pictures/karakal_logo_grey.icns" \
    --add-data="assets:assets" \
    --add-data="pictures:pictures" \
    main.py

# Pokud nemáš .icns, vytvoř z PNG
# mkdir tmp.iconset
# sips -z 16 16 pictures/karakal_logo_grey.png --out tmp.iconset/icon_16x16.png
# sips -z 32 32 pictures/karakal_logo_grey.png --out tmp.iconset/icon_32x32.png
# sips -z 128 128 pictures/karakal_logo_grey.png --out tmp.iconset/icon_128x128.png
# sips -z 256 256 pictures/karakal_logo_grey.png --out tmp.iconset/icon_256x256.png
# sips -z 512 512 pictures/karakal_logo_grey.png --out tmp.iconset/icon_512x512.png
# iconutil -c icns tmp.iconset
# mv tmp.icns pictures/karakal_logo_grey.icns
```

### 📦 DMG instalátor
```bash
# Nainstaluj create-dmg
brew install create-dmg

# Vytvoř DMG
create-dmg \
    --volname "Reservation System" \
    --window-pos 200 120 \
    --window-size 600 300 \
    --icon-size 100 \
    --icon "ReservationSystem.app" 175 120 \
    --hide-extension "ReservationSystem.app" \
    --app-drop-link 425 120 \
    "ReservationSystem.dmg" \
    "dist/"
```

**Výsledek:** `ReservationSystem.dmg` (~50MB)

### 🧪 Test macOS .app
```bash
# Test .app
open dist/ReservationSystem.app

# Test DMG
open ReservationSystem.dmg
```

### ⚠️ Řešení problémů macOS
```bash
# Pokud macOS blokuje neidentifikovaného vývojáře
sudo spctl --master-disable

# Nebo přidej výjimku pro konkrétní app
sudo xattr -rd com.apple.quarantine dist/ReservationSystem.app

# Pro distribuci - podepíš aplikaci
# (vyžaduje Apple Developer Account)
# codesign --deep --force --verify --verbose --sign "Developer ID Application: Your Name" dist/ReservationSystem.app
```

---

## 🔄 AUTOMATIZACE BUILDŮ

### ☁️ GitHub Actions (doporučeno)

Pro automatické buildy všech platforem současně máme připravený GitHub Actions workflow:

**Umístění:** `.github/workflows/build.yml`

**Jak použít:**
1. Push kód na GitHub: `git push origin master`
2. GitHub automaticky builduje Windows, macOS, Linux
3. Stáhni hotové soubory z **Actions** → **Artifacts**

**Manuální spuštění:**
- GitHub repo → **Actions** → **Multi-Platform Build** → **Run workflow**

### Windows batch script
```batch
@echo off
echo Building Windows executable...
& "C:/Program Files/Python38/python.exe" -m PyInstaller --onefile --noconsole --name "ReservationSystem" --icon="pictures\karakal_logo_grey.ico" --add-data="assets;assets" --add-data="pictures;pictures" main.py
echo Build complete: dist\ReservationSystem.exe
pause
```

### Linux build script
```bash
#!/bin/bash
echo "Building Linux binary..."
pyinstaller --onefile --name "ReservationSystem" main.py
echo "Build complete: dist/ReservationSystem"
```

### macOS build script
```bash
#!/bin/bash
echo "Building macOS app..."
pyinstaller --onefile --windowed --name "ReservationSystem" main.py
echo "Build complete: dist/ReservationSystem.app"
```

---

## 📊 POROVNÁNÍ VÝSTUPŮ

| Platform | Soubor | Velikost | Spuštění | Distribuce |
|----------|--------|----------|----------|------------|
| **Windows** | `.exe` | ~45MB | 5-10s | Kopíruj .exe |
| **Linux** | `binary` | ~40MB | 2-5s | Kopíruj binary |
| **Linux** | `.AppImage` | ~40MB | 3-6s | Kopíruj .AppImage |
| **macOS** | `.app` | ~50MB | 3-7s | Kopíruj .app |
| **macOS** | `.dmg` | ~50MB | 3-7s | Spusť .dmg |

---

## ✅ FINÁLNÍ CHECKLIST

### Před buildem:
- [ ] Aplikace funguje v dev módu (`python main.py`)
- [ ] Všechny závislosti v `requirements.txt`
- [ ] Testován databázový a chat funkcionality
- [ ] Ikony připraveny pro každou platformu

### Po buildu:
- [ ] Spouštěcí soubor funguje na čisté platformě
- [ ] Konfigurace se ukládá na správné místo
- [ ] Chat a databáze funkční
- [ ] Auto-refresh a všechny features работают

### Distribuce:
- [ ] Vytvořen instalační balíček
- [ ] README pro uživatele
- [ ] Systémové požadavky zdokumentovány

---

**Vytvořeno:** 2.9.2025  
**Status:** 🟢 Ready for production builds

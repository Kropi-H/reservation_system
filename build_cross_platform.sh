#!/bin/bash
# Cross-platform build script pro ReservationSystem
# Podporuje: Linux, macOS

echo "🌍 Cross-Platform Build Script pro ReservationSystem"
echo "===================================================="

# Detekce OS
OS=""
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    OS="Linux"
    echo "🐧 Detekován Linux"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    OS="macOS"
    echo "🍎 Detekován macOS"
else
    echo "❌ Nepodporovaný OS: $OSTYPE"
    exit 1
fi

# Kontrola závislostí
echo "📋 Kontroluji závislosti..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 není nainstalován"
    if [[ $OS == "Linux" ]]; then
        echo "Spusť: sudo apt install python3 python3-pip python3-venv"
    else
        echo "Nainstaluj Python 3.8+ z https://python.org"
    fi
    exit 1
fi

# Linux specifické závislosti
if [[ $OS == "Linux" ]]; then
    echo "📦 Kontroluji Linux systémové knihovny..."
    sudo apt update -qq
    sudo apt install -y \
        libxcb-xinerama0 libxcb1 libx11-6 libxrandr2 libxss1 \
        libxcursor1 libxdamage1 libxfixes3 libxcomposite1 \
        libxi6 libxtst6 libgl1-mesa-glx
fi

# macOS specifické závislosti
if [[ $OS == "macOS" ]]; then
    echo "🔧 Kontroluji macOS nástroje..."
    if ! command -v iconutil &> /dev/null; then
        echo "❌ Xcode Command Line Tools nejsou nainstalovány"
        echo "Spusť: xcode-select --install"
        exit 1
    fi
fi

# Vytvoř virtuální prostředí
echo "🐍 Vytvářím Python prostředí..."
python3 -m venv venv
source venv/bin/activate

# Nainstaluj Python závislosti
echo "📥 Instaluji Python závislosti..."
pip install --upgrade pip
pip install -r requirements.txt
pip install pyinstaller

# Test nových modulů před buildem
echo "🔍 Testuji nové real-time notifikace moduly..."
python3 -c "
import sys
try:
    import models.database_listener
    print('✅ database_listener import OK')
except ImportError as e:
    print(f'❌ database_listener import failed: {e}')
    sys.exit(1)

try:
    from views.hlavni_okno import HlavniOkno
    print('✅ HlavniOkno with real-time notifications import OK')
except ImportError as e:
    print(f'❌ HlavniOkno import failed: {e}')
    sys.exit(1)

try:
    from models.ordinace import add_ordinace, update_ordinace_db, remove_ordinace
    print('✅ ordinace notifications import OK')
except ImportError as e:
    print(f'❌ ordinace notifications failed: {e}')
    sys.exit(1)

try:
    from models.doktori import add_doctor, update_doctor, deactivate_doctor, remove_doctor
    print('✅ doktori notifications import OK')
except ImportError as e:
    print(f'❌ doktori notifications failed: {e}')
    sys.exit(1)

print('🎉 Všechny nové moduly pro real-time notifikace fungují!')
" || exit 1

# macOS ikona
if [[ $OS == "macOS" ]]; then
    echo "🖼️ Vytvářím ICNS ikonu..."
    if [ ! -f "pictures/karakal_logo_grey.icns" ]; then
        echo "Vytvářím .icns soubor z PNG..."
        mkdir -p tmp.iconset
        
        # Vytvoř různé velikosti ikon
        sips -z 16 16 pictures/karakal_logo_grey.png --out tmp.iconset/icon_16x16.png
        sips -z 32 32 pictures/karakal_logo_grey.png --out tmp.iconset/icon_32x32.png
        sips -z 128 128 pictures/karakal_logo_grey.png --out tmp.iconset/icon_128x128.png
        sips -z 256 256 pictures/karakal_logo_grey.png --out tmp.iconset/icon_256x256.png
        sips -z 512 512 pictures/karakal_logo_grey.png --out tmp.iconset/icon_512x512.png
        
        # Vytvoř ICNS soubor
        iconutil -c icns tmp.iconset
        mv tmp.icns pictures/karakal_logo_grey.icns
        
        # Ukliď
        rm -rf tmp.iconset
        echo "✅ ICNS ikona vytvořena"
    else
        echo "✅ ICNS ikona již existuje"
    fi
fi

# Build aplikace
echo "🔨 Builduji $OS aplikaci s real-time notifikacemi..."
pyinstaller ReservationSystem.spec

# Zkontroluj výsledek podle OS
if [[ $OS == "Linux" ]]; then
    if [ -f "dist/ReservationSystem" ]; then
        echo "✅ Linux build úspěšný!"
        echo "📁 Soubor: $(pwd)/dist/ReservationSystem"
        echo "📊 Velikost: $(ls -lh dist/ReservationSystem | awk '{print $5}')"
        
        # Vytvoř .desktop soubor
        echo "🖼️ Vytvářím .desktop soubor..."
        cat > ReservationSystem.desktop << EOF
[Desktop Entry]
Type=Application
Name=Reservation System
Comment=Veterinary Reservation System with Real-time Sync
Exec=$(pwd)/dist/ReservationSystem
Icon=$(pwd)/pictures/karakal_logo_grey.png
Categories=Office;Database;
Terminal=false
EOF
        
        echo "🚀 Spuštění: chmod +x dist/ReservationSystem && ./dist/ReservationSystem"
        echo "🖼️ Ikona: desktop-file-install --dir=~/.local/share/applications ReservationSystem.desktop"
    else
        echo "❌ Linux build selhal!"
        exit 1
    fi
    
elif [[ $OS == "macOS" ]]; then
    if [ -d "dist/ReservationSystem.app" ]; then
        echo "✅ macOS build úspěšný!"
        echo "📁 Aplikace: $(pwd)/dist/ReservationSystem.app"
        echo "📊 Velikost: $(du -sh dist/ReservationSystem.app | awk '{print $1}')"
        
        # Nastavit executable permissions
        chmod +x dist/ReservationSystem.app/Contents/MacOS/ReservationSystem
        
        echo "🚀 Instalace: cp -r dist/ReservationSystem.app /Applications/"
        echo "🔐 První spuštění: xattr -dr com.apple.quarantine /Applications/ReservationSystem.app"
    else
        echo "❌ macOS build selhal!"
        exit 1
    fi
fi

echo ""
echo "🎉 Build dokončen! Aplikace obsahuje:"
echo "   ✅ Real-time synchronizaci rezervací"  
echo "   ✅ Real-time synchronizaci doktorů"
echo "   ✅ Real-time synchronizaci ordinací"
echo "   ✅ Multi-instance notifikace"
echo "   ✅ PostgreSQL NOTIFY/LISTEN systém"

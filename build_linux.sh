#!/bin/bash
# Linux build script pro Ubuntu/Mint

echo "🐧 Linux Build Script pro ReservationSystem"
echo "============================================"

# Kontrola závislostí
echo "📋 Kontroluji závislosti..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 není nainstalován"
    sudo apt install python3 python3-pip python3-venv
fi

# Nainstaluj systémové knihovny
echo "📦 Instaluji systémové knihovny..."
sudo apt update
sudo apt install -y \
    libxcb-xinerama0 libxcb1 libx11-6 libxrandr2 libxss1 \
    libxcursor1 libxdamage1 libxfixes3 libxcomposite1 \
    libxi6 libxtst6 libgl1-mesa-glx

# Vytvoř virtuální prostředí
echo "🐍 Vytvářím Python prostředí..."
python3 -m venv venv
source venv/bin/activate

# Nainstaluj Python závislosti
echo "📥 Instaluji Python závislosti..."
pip install --upgrade pip
pip install -r requirements.txt
pip install pyinstaller

# Build binary
echo "🔨 Builduji Linux binary..."
# Poznámka: --icon není podporováno na Linuxu, ikona se nastavuje přes desktop integration
pyinstaller --onefile --name "ReservationSystem" \
    --add-data="assets:assets" \
    --add-data="pictures:pictures" \
    main.py

# Zkontroluj výsledek
if [ -f "dist/ReservationSystem" ]; then
    echo "✅ Build úspěšný!"
    echo "📁 Soubor: $(pwd)/dist/ReservationSystem"
    echo "📊 Velikost: $(ls -lh dist/ReservationSystem | awk '{print $5}')"
    
    # Vytvoř .desktop soubor pro ikonu
    echo "🖼️ Vytvářím .desktop soubor pro ikonu..."
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
    
    echo "📋 Vytvořen: ReservationSystem.desktop"
    echo ""
    echo "🚀 Spuštění:"
    echo "chmod +x dist/ReservationSystem"
    echo "./dist/ReservationSystem"
    echo ""
    echo "🖼️ Pro ikonu v systému (optional):"
    echo "desktop-file-install --dir=~/.local/share/applications ReservationSystem.desktop"
else
    echo "❌ Build selhal!"
    exit 1
fi

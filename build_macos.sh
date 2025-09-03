#!/bin/bash
# macOS build script pro ReservationSystem

echo "🍎 macOS Build Script pro ReservationSystem"
echo "============================================"

# Kontrola závislostí
echo "📋 Kontroluji závislosti..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 není nainstalován"
    echo "Nainstaluj Python 3.8+ z https://python.org"
    exit 1
fi

# Kontrola Xcode Command Line Tools
if ! command -v iconutil &> /dev/null; then
    echo "❌ Xcode Command Line Tools nejsou nainstalovány"
    echo "Spusť: xcode-select --install"
    exit 1
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

# Test importů před buildem + macOS specifické testy
echo "🔍 Testuji nové moduly a macOS kompatibilitu..."
python3 -c "
try:
    import models.database_listener
    print('✅ database_listener import OK')
except ImportError as e:
    print(f'❌ database_listener import failed: {e}')
    exit(1)

try:
    import models.connection_pool
    print('✅ connection_pool import OK')
except ImportError as e:
    print(f'❌ connection_pool import failed: {e}')
    exit(1)

try:
    from views.hlavni_okno import HlavniOkno
    print('✅ HlavniOkno with new features import OK')
except ImportError as e:
    print(f'❌ HlavniOkno import failed: {e}')
    exit(1)

# macOS specifické testy pro pooling
import platform
if platform.system() == 'Darwin':
    import select
    print('✅ select module OK')
    
    try:
        import psycopg2.pool
        print('✅ psycopg2.pool import OK')
    except ImportError as e:
        print(f'❌ psycopg2.pool import failed: {e}')
        exit(1)
    
    try:
        # Test krátký select call
        select.select([], [], [], 0.1)
        print('✅ select.select() funguje')
    except Exception as e:
        print(f'⚠️ select.select() může mít problémy: {e}')
        print('🍎 Použije se polling fallback')

print('🎉 Všechny kontroly prošly!')
" || exit 1

# Vytvoř ICNS ikonu z PNG
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

# Build aplikace
echo "🔨 Builduji macOS aplikaci..."
pyinstaller ReservationSystem.spec

# Zkontroluj výsledek
if [ -d "dist/ReservationSystem.app" ]; then
    echo "✅ Build úspěšný!"
    echo "📁 Aplikace: $(pwd)/dist/ReservationSystem.app"
    echo "📊 Velikost: $(du -sh dist/ReservationSystem.app | awk '{print $1}')"
    
    # Zkontroluj, jestli je executable
    if [ -x "dist/ReservationSystem.app/Contents/MacOS/ReservationSystem" ]; then
        echo "✅ Executable je správně nastaven"
    else
        echo "⚠️ Nastavuji executable permissions..."
        chmod +x dist/ReservationSystem.app/Contents/MacOS/ReservationSystem
    fi
    
    echo ""
    echo "🚀 Instalace:"
    echo "cp -r dist/ReservationSystem.app /Applications/"
    echo ""
    echo "🔐 První spuštění (bezpečnost):"
    echo "xattr -dr com.apple.quarantine /Applications/ReservationSystem.app"
    echo "open /Applications/ReservationSystem.app"
    echo ""
    echo "📦 Vytvoření DMG (optional):"
    echo "hdiutil create -volname 'ReservationSystem' -srcfolder dist/ReservationSystem.app -ov -format UDZO ReservationSystem.dmg"
    
    # Optional: Automaticky zkopíruj do Applications (pokud máme práva)
    if [ -w "/Applications" ]; then
        read -p "Chceš automaticky nainstalovat do /Applications? (y/n): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            cp -r dist/ReservationSystem.app /Applications/
            echo "✅ Aplikace nainstalována do /Applications/"
            
            # Odstraň quarantine
            xattr -dr com.apple.quarantine /Applications/ReservationSystem.app 2>/dev/null || true
            echo "✅ Quarantine odstraněn"
        fi
    fi
    
else
    echo "❌ Build selhal!"
    exit 1
fi

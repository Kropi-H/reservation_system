# 🍎 macOS Installation Guide - ReservationSystem

Tento guide popisuje různé způsoby instalace a distribuce ReservationSystem aplikace na macOS platformě.

## 📋 Obsah
- [Požadavky](#požadavky)
- [Automatický build (GitHub Actions)](#automatický-build-github-actions)
- [Lokální build](#lokální-build)
- [Instalace z .app](#instalace-z-app)
- [Code Signing & Notarization](#code-signing--notarization)
- [Distribuce](#distribuce)
- [Troubleshooting](#troubleshooting)

## 🔧 Požadavky

### Systémové požadavky
- macOS 10.14 (Mojave) nebo novější
- Python 3.8-3.11
- Xcode Command Line Tools (pro lokální build)

### Pro koncové uživatele
- Žádné speciální požadavky
- Aplikace je standalone (obsahuje všechny závislosti)

## 🤖 Automatický build (GitHub Actions)

**Nejjednodušší způsob** - build probíhá automaticky při každém push do main branch.

### 1. Stažení z GitHub Actions
```bash
# Přejdi na: https://github.com/Kropi-H/reservation_system/actions
# Klikni na nejnovější úspěšný build
# Stáhni "ReservationSystem-macOS" artifact
```

### 2. Rozbalení a instalace
```bash
# Rozbal stažený ZIP
unzip ReservationSystem-macOS.zip

# Přesuň do Applications
mv ReservationSystem.app /Applications/

# První spuštění (viz bezpečnost níže)
```

## 🛠️ Lokální build

### 1. Příprava prostředí
```bash
# Klonuj repository
git clone https://github.com/Kropi-H/reservation_system.git
cd reservation_system

# Vytvoř virtuální prostředí
python3 -m venv venv
source venv/bin/activate

# Nainstaluj závislosti
pip install -r requirements.txt
pip install pyinstaller
```

### 2. Vytvoření ikony (automaticky)
```bash
# GitHub Actions workflow automaticky vytváří .icns soubor z PNG
# Pro lokální build:
mkdir tmp.iconset
sips -z 16 16 pictures/karakal_logo_grey.png --out tmp.iconset/icon_16x16.png
sips -z 32 32 pictures/karakal_logo_grey.png --out tmp.iconset/icon_32x32.png
sips -z 128 128 pictures/karakal_logo_grey.png --out tmp.iconset/icon_128x128.png
sips -z 256 256 pictures/karakal_logo_grey.png --out tmp.iconset/icon_256x256.png
sips -z 512 512 pictures/karakal_logo_grey.png --out tmp.iconset/icon_512x512.png
iconutil -c icns tmp.iconset
mv tmp.icns pictures/karakal_logo_grey.icns
```

### 3. Build aplikace
```bash
# Použij unified .spec soubor
pyinstaller ReservationSystem.spec

# Nebo čistý build
pyinstaller --clean ReservationSystem.spec
```

**Výsledek:** `dist/ReservationSystem.app` (~45MB)

## 📱 Instalace z .app

### 1. Základní instalace
```bash
# Zkopíruj do Applications
cp -r dist/ReservationSystem.app /Applications/

# Nebo přetažením v Finderu
```

### 2. První spuštění (bezpečnost)
macOS může blokovat aplikaci kvůli bezpečnosti:

```bash
# Pokud se zobrazí varování o neznámém vývojáři:
# 1. Klikni pravým na ReservationSystem.app
# 2. Vyber "Open" (ne "Open With")
# 3. Klikni "Open" v dialogu

# Nebo přes terminál:
xattr -dr com.apple.quarantine /Applications/ReservationSystem.app
```

### 3. Ověření instalace
```bash
# Zkontroluj, že se app spustí
open /Applications/ReservationSystem.app

# Zkontroluj verzi (pokud je implementována)
/Applications/ReservationSystem.app/Contents/MacOS/ReservationSystem --version
```

## 🔐 Code Signing & Notarization

Pro profesionální distribuci potřebuješ Apple Developer Account.

### 1. Code Signing
```bash
# S Apple Developer Account
codesign --force --deep --sign "Developer ID Application: Your Name" ReservationSystem.app

# Ověření
codesign --verify --deep --strict ReservationSystem.app
spctl -a -t exec -v ReservationSystem.app
```

### 2. Notarization
```bash
# Vytvoř ZIP pro notarization
ditto -c -k --keepParent ReservationSystem.app ReservationSystem.zip

# Pošli k notarization
xcrun notarytool submit ReservationSystem.zip --apple-id your@email.com --password app-specific-password --team-id TEAM_ID --wait

# Staple výsledek
xcrun stapler staple ReservationSystem.app
```

### 3. GitHub Actions s Code Signing
```yaml
# Přidej do .github/workflows/build.yml pro macOS job:
- name: Import certificates
  env:
    BUILD_CERTIFICATE_BASE64: ${{ secrets.BUILD_CERTIFICATE_BASE64 }}
    P12_PASSWORD: ${{ secrets.P12_PASSWORD }}
  run: |
    echo $BUILD_CERTIFICATE_BASE64 | base64 --decode > certificate.p12
    security create-keychain -p "" build.keychain
    security import certificate.p12 -k build.keychain -P $P12_PASSWORD
    security unlock-keychain -p "" build.keychain

- name: Sign app
  run: |
    codesign --force --deep --sign "Developer ID Application: Your Name" dist/ReservationSystem.app
```

## 📦 Distribuce

### 1. Direct Download
```bash
# Vytvoř komprimovaný ZIP
ditto -c -k --keepParent ReservationSystem.app ReservationSystem-macOS.zip

# Upload na server nebo GitHub Releases
```

### 2. DMG balíček (doporučeno)
```bash
# Vytvoř DMG pro profesionální distribuci
hdiutil create -volname "ReservationSystem" -srcfolder ReservationSystem.app -ov -format UDZO ReservationSystem.dmg

# S pozadím a stylem
mkdir dmg_temp
cp -r ReservationSystem.app dmg_temp/
# ... přidej pozadí, styly atd.
hdiutil create -volname "ReservationSystem" -srcfolder dmg_temp -ov -format UDZO ReservationSystem.dmg
```

### 3. Homebrew Cask (pro open source)
```ruby
# Formula pro homebrew-cask
cask "reservation-system" do
  version "1.0.0"
  sha256 "checksum_here"
  
  url "https://github.com/Kropi-H/reservation_system/releases/download/v#{version}/ReservationSystem-macOS.zip"
  name "Reservation System"
  desc "Veterinary reservation management system"
  homepage "https://github.com/Kropi-H/reservation_system"
  
  app "ReservationSystem.app"
end
```

## 🔧 Konfigurace pro macOS

### Cesty k souborům
```python
# Automaticky detekováno v aplikaci:
# ~/Library/Application Support/ReservationSystem/
# ~/Library/Application Support/ReservationSystem/chat_config.json
```

### Síťové nastavení
```bash
# PostgreSQL připojení
# Aplikace se pokusí připojit k nastaveným adresám
# Konfigurace přes GUI nebo config soubory
```

## 🐛 Troubleshooting

### 1. Aplikace se nespustí
```bash
# Zkontroluj permissions
ls -la /Applications/ReservationSystem.app/Contents/MacOS/ReservationSystem
chmod +x /Applications/ReservationSystem.app/Contents/MacOS/ReservationSystem

# Zkontroluj quarantine
xattr -l /Applications/ReservationSystem.app
xattr -dr com.apple.quarantine /Applications/ReservationSystem.app
```

### 2. Chybí PostgreSQL závislosti
```bash
# Aplikace obsahuje psycopg2-binary, ale může potřebovat:
brew install postgresql  # pouze klientské knihovny
```

### 3. Síťové problémy
```bash
# Zkontroluj firewall
sudo pfctl -sr | grep 5432
sudo pfctl -f /etc/pf.conf

# Zkontroluj připojení
telnet your-postgres-server 5432
```

### 4. Problémy s ikonou
```bash
# Znovu vytvoř icns soubor
rm pictures/karakal_logo_grey.icns
# ... znovu spusť icon creation script
```

### 5. Console output pro debugging
```bash
# Spusť z terminálu pro vidění chyb
/Applications/ReservationSystem.app/Contents/MacOS/ReservationSystem

# Nebo zkontroluj log
tail -f /var/log/system.log | grep ReservationSystem
```

## 📋 Checklist pro distribuci

### Pre-release
- [ ] Testováno na různých verzích macOS (10.14+)
- [ ] Ikona se zobrazuje správně
- [ ] Aplikace se spouští bez konzole
- [ ] Všechny funkce fungují
- [ ] Konfigurace se ukládá správně

### Release
- [ ] Code signing (pokud máš Apple Developer Account)
- [ ] Notarization (pro distribuci mimo App Store)
- [ ] DMG soubor vytvořen
- [ ] GitHub Release vytvořen
- [ ] Dokumentace aktualizována

### Post-release
- [ ] Testování na různých macOS verzích
- [ ] User feedback
- [ ] Monitoring crash reports
- [ ] Update dokumentace dle potřeby

## 🚀 Quick Start pro uživatele

1. **Stažení:** Stáhni nejnovější release z GitHub
2. **Instalace:** Přetáhni `ReservationSystem.app` do `Applications`
3. **První spuštění:** Klikni pravým na app → Open → Open
4. **Konfigurace:** Nastav PostgreSQL připojení v aplikaci
5. **Hotovo:** Aplikace je připravena k použití!

---

**Poznámka:** Tento guide předpokládá použití unified `ReservationSystem.spec` souboru, který automaticky detekuje macOS a vytváří správnou .app strukturu s ikonami.

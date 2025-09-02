# 🤖 GITHUB ACTIONS - Automatické buildy

## 📋 Přehled

GitHub Actions automaticky vytváří spouštěcí soubory pro všechny platformy při každém push na GitHub.

| Platform | Výstup | Velikost | Auto Build |
|----------|--------|----------|------------|
| **Windows** | `ReservationSystem.exe` | ~45MB | ✅ |
| **macOS** | `ReservationSystem.app` | ~50MB | ✅ |
| **Linux** | `ReservationSystem` | ~40MB | ✅ |

---

## ⚙️ KONFIGURACE

### 📁 Workflow soubor
**Umístění:** `.github/workflows/build.yml`

**Triggers:**
- Push na `master` branch
- Pull request na `master`
- Manuální spuštění přes GitHub UI

---

## 🚀 POUŽITÍ

### 1. **Automatický build:**
```bash
# Commitni změny
git add .
git commit -m "Update application"
git push origin master

# GitHub automaticky spustí build pro všechny platformy
```

### 2. **Manuální build:**
1. Jdi na GitHub repo: `https://github.com/Kropi-H/reservation_system`
2. Klikni na **Actions** tab
3. Vyber **Multi-Platform Build**
4. Klikni **Run workflow** → **Run workflow**

### 3. **Stažení buildů:**
1. Jdi na **Actions** tab
2. Klikni na nejnovější build (zelený ✅)
3. Stáhni **Artifacts**:
   - `ReservationSystem-Windows.zip` → obsahuje `.exe`
   - `ReservationSystem-macOS.zip` → obsahuje `.app`
   - `ReservationSystem-Linux.zip` → obsahuje binary

---

## 📊 BUILD DETAILY

### 🖥️ Windows Build
```yaml
- runs-on: windows-latest
- python: 3.8
- výstup: ReservationSystem.exe (~45MB)
- ikona: pictures/karakal_logo_grey.ico
- resources: assets/, pictures/
```

### 🍎 macOS Build
```yaml
- runs-on: macos-latest  
- python: 3.8
- ikona: automaticky vytvoří .icns z PNG
- výstup: ReservationSystem.app (~50MB)
- resources: assets/, pictures/
```

### 🐧 Linux Build
```yaml
- runs-on: ubuntu-latest
- python: 3.8
- system libs: Qt knihovny pro GUI
- výstup: ReservationSystem binary (~40MB)
- resources: assets/, pictures/
```

---

## 🔧 TROUBLESHOOTING

### ❌ Build selhává?

**1. Zkontroluj dependencies:**
```yaml
# V requirements.txt musí být všechny potřebné balíčky
PySide6==6.6.3.1
psycopg2-binary==2.9.9
# ... ostatní
```

**2. Zkontroluj chybějící soubory:**
```yaml
# V build.yml jsou správné cesty?
--add-data="assets:assets"
--add-data="pictures:pictures"
--icon="pictures/karakal_logo_grey.ico"  # Windows
--icon="pictures/karakal_logo_grey.icns" # macOS
```

**3. Zkontroluj Python kompatibilitu:**
```yaml
# Všechny platformy používají Python 3.8
python-version: '3.8'
```

### 🔍 Debug buildu

**1. Zobraz build logy:**
- Actions → klikni na konkrétní build → rozbal failed step

**2. Lokální test před push:**
```bash
# Windows
& "C:/Program Files/Python38/python.exe" -m PyInstaller --onefile --noconsole --name "ReservationSystem" --icon="pictures\karakal_logo_grey.ico" --add-data="assets;assets" --add-data="pictures;pictures" main.py

# Test že .exe funguje
.\dist\ReservationSystem.exe
```

---

## 💡 VÝHODY GITHUB ACTIONS

### ✅ Pro projekty
- **Automatizace:** Push → build → download
- **Multi-platform:** Windows + macOS + Linux současně
- **Zdarma:** Pro public repositories
- **Konzistentní:** Stejné prostředí při každém buildu
- **Rychlé:** Paralelní buildy (~5-10 minut celkem)

### ✅ Pro distribuci
- **Artifacts:** Zip soubory ke stažení
- **Verze:** Každý build má své číslo
- **Release:** Automatické vydání nových verzí
- **Download linky:** Přímé stažení pro uživatele

---

## 🎯 POKROČILÉ FUNKCE

### 📦 Automatické releases
```yaml
# Přidej do build.yml pro automatické releases při tagu
- name: Create Release
  if: startsWith(github.ref, 'refs/tags/')
  uses: actions/create-release@v1
```

### 🏷️ Vytvoření tagu
```bash
# Lokálně označ verzi
git tag v1.0.0
git push origin v1.0.0

# GitHub automaticky vytvoří release s buildy
```

### 📝 Build badge
```markdown
# Do README.md přidej badge
![Build Status](https://github.com/Kropi-H/reservation_system/workflows/Multi-Platform%20Build/badge.svg)
```

---

## 📋 CHECKLIST

### Před použitím:
- [ ] Workflow soubor je v `.github/workflows/build.yml`
- [ ] `requirements.txt` obsahuje všechny závislosti
- [ ] Ikony existují: `pictures/karakal_logo_grey.ico` (Windows)
- [ ] Assets složky existují: `assets/`, `pictures/`
- [ ] Aplikace funguje lokálně: `python main.py`

### Po buildu:
- [ ] Všechny 3 platformy buildují úspěšně
- [ ] Artifacts jsou ke stažení
- [ ] .exe/.app/binary soubory fungují
- [ ] Velikosti souborů jsou rozumné (~40-50MB)

---

**Vytvořeno:** 2.9.2025  
**Status:** 🟢 Aktivní a funkční  
**Repo:** https://github.com/Kropi-H/reservation_system

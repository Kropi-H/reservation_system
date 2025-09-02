# ⚠️ GitHub Actions - Dočasně vypnuté

## 🔍 Důvod deaktivace

GitHub Actions automatické buildy byly dočasně vypnuté kvůli problému s logy aplikace:
- **Problém:** Logo se zobrazuje správně pouze při lokálním Windows buildu
- **GitHub Actions:** Loga nefungují v automatizovaných buildech
- **Řešení:** Používej lokální build pro správné zobrazení log

## 🛠️ Jak buildovat lokálně

### Windows
```powershell
# Aktivuj virtuální prostředí
.\venv\Scripts\Activate.ps1

# Build s logy
pyinstaller ReservationSystem.spec
```

### macOS
```bash
# Použij build script
chmod +x build_macos.sh
./build_macos.sh
```

### Linux
```bash
# Použij build script
chmod +x build_linux.sh
./build_linux.sh
```

## 🔄 Jak znovu aktivovat GitHub Actions

Pokud se problém s logy vyřeší, můžeš znovu aktivovat automatické buildy:

1. **Edituj `.github/workflows/build.yml`**
2. **Odkomentuj triggers:**
   ```yaml
   on:
     push:
       branches: [ master ]
     pull_request:
       branches: [ master ]
     workflow_dispatch:
   ```
3. **Commit a push změny**

## 📋 Status

- ❌ **GitHub Actions:** Vypnuté (logo issues)
- ✅ **Lokální Windows build:** Funguje s logy
- ✅ **Lokální macOS build:** Funguje
- ✅ **Lokální Linux build:** Funguje
- ✅ **Manual trigger:** Stále dostupný přes workflow_dispatch

## 🚀 Doporučení

Pro nejlepší výsledky používej **lokální build** na své platformě, dokud se problém s GitHub Actions nevyřeší.

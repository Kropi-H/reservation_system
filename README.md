# 🏥 Rezervační systém veteriny

Kompletní rezervační systém pro veterinární ordinace s podporou více platforem, real-time synchronizací a chat funkcionalitou.

## 🚀 Rychlý start

### 📥 Spouštěcí soubory (lokální build doporučen)
> ⚠️ **Poznámka:** Automatické GitHub Actions buildy jsou dočasně vypnuté kvůli problémům s logy. Doporučujeme lokální build.

- **Windows:** Lokální build s `pyinstaller ReservationSystem.spec`
- **macOS:** Použij [build_macos.sh](build_macos.sh) nebo [MACOS_INSTALLATION.md](MACOS_INSTALLATION.md)
- **Linux:** Použij [build_linux.sh](build_linux.sh)

### 🔧 Lokální build (doporučeno)
- **Multi-platform:** [CROSS_PLATFORM_BUILD.md](CROSS_PLATFORM_BUILD.md) - kompletní návod
- **macOS specificky:** [MACOS_INSTALLATION.md](MACOS_INSTALLATION.md) - detailní macOS guide
- **Quick build:** `pyinstaller ReservationSystem.spec`

# Run aplikace
python main.py
```

## 📚 Dokumentace

| Soubor | Popis |
|--------|-------|
| [`CROSS_PLATFORM_BUILD.md`](CROSS_PLATFORM_BUILD.md) | Návod na vytváření .exe/.app/binary souborů |
| [`CROSS_PLATFORM_CONFIG.md`](CROSS_PLATFORM_CONFIG.md) | Konfigurace pro Windows/macOS/Linux + PostgreSQL |
| [`GITHUB_ACTIONS_NAVOD.md`](GITHUB_ACTIONS_NAVOD.md) | Automatické buildy přes GitHub Actions |

## 🎯 Funkce

- ✅ **Cross-platform:** Windows, macOS, Linux
- ✅ **PostgreSQL databáze** s network podporou
- ✅ **Real-time synchronizace** mezi více instancemi
- ✅ **Chat systém** pro komunikaci
- ✅ **Auto-refresh** každých 30 sekund (F5/Ctrl+R)
- ✅ **Professional konfigurace** podle OS standardů

## ⚙️ Konfigurace

### Windows
```
%LOCALAPPDATA%\ReservationSystem\
├── config.json          # Databáze
└── chat_config.json     # Chat
```

### macOS  
```
~/Library/Application Support/ReservationSystem/
├── config.json          # Databáze
└── chat_config.json     # Chat
```

### Linux
```
~/.config/ReservationSystem/
├── config.json          # Databáze  
└── chat_config.json     # Chat
```

## 🔧 Systémové požadavky

| Platform | Požadavky |
|----------|-----------|
| **Windows** | Windows 10/11 (64-bit) |
| **macOS** | macOS 10.14+ |  
| **Linux** | Ubuntu 18.04+ / Debian 10+ |
| **Databáze** | PostgreSQL 12+ |
| **RAM** | 512MB+ |
| **Disk** | 100MB+ |

## 👥 Přispívání

1. Fork repository
2. Vytvoř feature branch (`git checkout -b feature/nova-funkce`)
3. Commit změny (`git commit -am 'Přidej novou funkci'`)
4. Push na branch (`git push origin feature/nova-funkce`)
5. Vytvoř Pull Request

## 📄 Licence

Tento projekt je licencován pod MIT licencí.

## 🆘 Podpora

- **Issues:** [GitHub Issues](https://github.com/Kropi-H/reservation_system/issues)
- **Dokumentace:** [Wiki](https://github.com/Kropi-H/reservation_system/wiki)
- **Buildy:** [Actions](https://github.com/Kropi-H/reservation_system/actions)

---

**Vytvořeno s ❤️ pro veterinární ordinace**
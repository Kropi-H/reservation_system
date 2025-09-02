# Test macOS Menu Bar - Návod k testování

## ✅ Implementované změny pro macOS

1. **Nativní menu bar**: `setNativeMenuBar(True)` aktivuje systémový menu bar
2. **Správná struktura menu**: Používáme `QMenu` místo přímých akcí
3. **Platform-specific handling**: Rozdílné chování pro macOS vs ostatní platformy
4. **Debug výstupy**: Sledování vytváření menu pro ladění

## 🔍 Kde hledat menu na macOS

**DŮLEŽITÉ**: Na macOS se menu nezobrazuje v okně aplikace, ale v **systémovém menu baru** nahoře na obrazovce!

### Kde najít menu:
1. **Horní lišta systému**: Menu se objeví vedle Apple logo, času atd.
2. **Název aplikace**: Měli byste vidět "ReservationSystem" v menu baru
3. **Menu položky**: 
   - "ReservationSystem" → obsahuje "Přihlášení"
   - "Úpravy" → bude obsahovat další akce po přihlášení

## 🧪 Testovací kroky

### 1. Spuštění aplikace
```bash
cd /path/to/reservation_system
python main.py
```

### 2. Kontrola debug výstupů
Sledujte konzoli pro tyto zprávy:
- `🍎 Detekováno macOS - používám nativní menu bar`
- `🍎 macOS menu vytvořeno: ReservationSystem`
- `🍎 macOS menu vytvořeno: Úpravy`

### 3. Hledání menu
- **Podívejte se na HORNÍ lištu obrazovky** (ne do okna aplikace)
- Měli byste vidět "ReservationSystem" vedle ostatních systémových menu
- Klikněte na "ReservationSystem" → měli byste vidět "Přihlášení"

### 4. Test přihlášení
1. Klikněte na "ReservationSystem" → "Přihlášení"
2. Přihlaste se pomocí admin účtu
3. Menu by se mělo změnit na "Odhlásit"
4. V "Úpravy" menu by se měly objevit další možnosti

## 🐛 Pokud menu není vidět

### Kontrolní seznam:
- [ ] Aplikace běží (okno je otevřené)
- [ ] Díváte se na HORNÍ lištu systému (ne do okna)
- [ ] V konzoli vidíte debug zprávy s 🍎
- [ ] Zkuste kliknout na různá místa v horní liště

### Debug informace:
Pokud stále není menu vidět, spusťte s debug výstupem:
```bash
python main.py 2>&1 | grep "🍎\|menu\|Menu"
```

## 🔧 Pro vývojáře

### Struktura menu na macOS:
```python
# V create_menu_bar():
if platform.system() == "Darwin":
    self.menu_bar.setNativeMenuBar(True)
    
    # Hlavní menu aplikace
    app_menu = self.menu_bar.addMenu("ReservationSystem")
    app_menu.addAction(self.login_action)
    
    # Editační menu
    edit_menu = self.menu_bar.addMenu("Úpravy")
    # Další akce se přidají po přihlášení
```

### Aktualizace akcí:
```python
# show_login_dialog() a logout_user() 
# mají platform-specific kód pro hledání a aktualizaci menu akcí
```

## 📝 Poznámky
- macOS menu bar chování je specifické a liší se od Windows/Linux
- Menu může být na začátku prázdné/neviditelné, dokud se nevytvoří správně
- Debug výstupy pomáhají sledovat, co se děje při vytváření menu

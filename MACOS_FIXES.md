# 🔧 Opravy pro macOS a multi-platform kompatibilitu

## 🖼️ Logo Display Fix

Problém s logem na různých platformách je způsoben relativními cestami v PyInstaller buildu.

### Původní problém:
```python
logo_path = os.path.join(os.path.dirname(__file__), "../pictures/karakal_logo_grey.png")
```

### Řešení:
Použití `sys._MEIPASS` pro PyInstaller a fallback na development cestu.

## 🍎 macOS Menu Bar Fix

Na macOS se menu automaticky přesouvá do systémového menu baru. Problém může být:
1. Menu není viditelné kvůli chybné inicializaci
2. Menu akce nejsou správně navázané
3. Aplikace nedetekuje správně macOS prostředí

### Řešení:
1. Explicitní nastavení native menu bar pro macOS
2. Přidání debug výpisů pro identifikaci problému
3. Fallback pro situation kdy menu není dostupné

## 🔧 Implementace oprav

Potřebné změny v `views/hlavni_okno.py`:

1. **Logo path fix** - resource path resolution
2. **macOS menu fix** - native menu bar handling  
3. **Debug output** - pro identifikaci problémů na různých platformách

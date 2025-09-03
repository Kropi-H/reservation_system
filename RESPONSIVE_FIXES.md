# 📱 Responzivní úpravy pro menší displeje

## 🎯 Provedené změny pro lepší zobrazení na MacBook 16"

### ✅ Nový layout struktura:
1. **Třířádkový layout** místo jednoho horizontálního řádku
2. **První řádek**: Logo + Hodiny (vždy viditelné)
3. **Druhý řádek**: Kalendář s navigačními tlačítky (vystředěné)
4. **Třetí řádek**: Legenda vakcinace/pauza (vystředěná)

### ✅ Optimalizované komponenty:

#### 🕐 Hodiny
- **Velikost**: 18px font (16px na menších obrazovkách)
- **Pozice**: Vpravo v prvním řádku
- **Zobrazení**: Vždy viditelné, kompaktní design

#### 📅 Kalendář
- **Responzivní velikost**: 150-200px (malé obrazovky) / 180-250px (velké)
- **Menší tlačítka**: 30x30px (malé) / 35x35px (velké)
- **Vystředěný** v druhém řádku

#### ✅ Checkboxy (ordinace + chat)
- **Kompaktní font**: 11px místo 12px
- **Menší spacing**: 5px místo 10px
- **Barevné indikátory**: Zelená (zapnuto) / Červená (vypnuto)
- **Omezenáý šířka**: 40-80px pro ordinace, 35-60px pro chat
- **Menší výška status baru**: maximálně 30px

#### 🏷️ Legenda
- **Kompaktní design**: 12px font, 3px padding
- **Menší velikost**: 60-80px šířka
- **Vlastní řádek**: Vystředěná pozice

### 🔧 Responzivní chování

#### Automatická detekce velikosti:
```python
def resizeEvent(self, event):
    window_width = self.width()
    
    if window_width < 1400:  # MacBook 16" rozlišení
        # Menší fonty a komponenty
    else:
        # Standardní velikosti
```

#### Breakpointy:
- **< 1400px**: Kompaktní režim (MacBook 16", menší notebooky)
- **≥ 1400px**: Standardní režim (velké monitory)

### 📏 Minimální velikost okna
- **Nová minimální velikost**: 1000x600px (místo větší)
- **Lepší zobrazení** na menších noteboocích

## 🧪 Testování na MacBook 16"

### Co byste teď měli vidět:
1. ✅ **Logo vlevo nahoře** (nebo "LOGO" placeholder)
2. ✅ **Hodiny vpravo nahoře** - stále viditelné
3. ✅ **Kalendář s tlačítky** - vystředěné, menší
4. ✅ **Legenda vakcinace/pauza** - vlastní řádek
5. ✅ **Checkboxy** - kompaktní v status baru, barevné indikátory

### Kontrolní kroky:
1. **Spusťte aplikaci**: `python3 main.py`
2. **Zkuste změnit velikost okna** - komponenty se automaticky přizpůsobí
3. **Zkontrolujte status bar** - checkboxy by měly být viditelné a kompaktní
4. **Testujte na malém a velkém okně** - fonty a velikosti se mění

## 🎨 Barevné kódování checkboxů

### Nový systém:
- **🟢 Zelený indikátor**: Ordinace/chat je zobrazena
- **🔴 Červený indikátor**: Ordinace/chat je skryta
- **Kompaktní text**: Kratší názvy pro úsporu místa

## 🔧 Pokud stále problémy

### Debug kroky:
1. **Zkontrolujte rozlišení**:
   ```bash
   python3 -c "
   from PySide6.QtWidgets import QApplication
   import sys
   app = QApplication(sys.argv)
   screen = app.primaryScreen()
   print(f'Rozlišení: {screen.size().width()}x{screen.size().height()}')
   print(f'Available: {screen.availableSize().width()}x{screen.availableSize().height()}')
   "
   ```

2. **Testujte změnu velikosti**: Táhněte za roh okna a sledujte změny

3. **Zkontrolujte konzoli**: Hledejte zprávy o velikosti loga a responzivních změnách

---

**Výsledek**: Aplikace by teď měla být plně funkční a čitelná i na MacBook 16" displeji! 🎉

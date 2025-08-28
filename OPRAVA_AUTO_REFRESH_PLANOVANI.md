# Oprava Auto-Refresh během plánování ordinačních časů

## Problém
Během plánování ordinačních časů doktorů se po 30 sekundách spouští auto-refresh, který znovu načte data z databáze a přepíše rozpracovanou práci uživatele.

## Příčina
Auto-refresh timer běží nepřetržitě každých 30 sekund bez ohledu na aktivitu uživatele.

## Řešení

### 1. Přidán tracking flag (`views/hlavni_okno.py`)
```python
def __init__(self):
    # Flag pro detekci aktivního plánování ordinačních časů
    self.is_planning_active = False
```

### 2. Pozastavení auto-refresh během plánování
```python
def auto_refresh_data(self):
    # Přeskočit auto-refresh pokud probíhá plánování ordinačních časů
    if self.is_planning_active:
        print("⏸️ Auto-refresh pozastaven - probíhá plánování ordinačních časů")
        return
    
    print("🔄 Auto-refresh dat...")
    self.nacti_rezervace()
```

### 3. Nastavení flag při spuštění plánování
```python
def zahaj_planovani_ordinaci(self):
    if dialog.exec():
        self.is_planning_active = True  # Nastavit flag - pozastavit auto-refresh
        print("📋 Plánování ordinačních časů spuštěno - auto-refresh pozastaven")
```

### 4. Reset flag při ukončení plánování
```python
def zrus_planovani(self):
    self.is_planning_active = False  # Obnovit auto-refresh
    print("✅ Plánování ordinačních časů ukončeno - auto-refresh obnoven")
```

## Výsledek
✅ Auto-refresh se pozastaví během aktivního plánování ordinačních časů
✅ Rozpracovaná práce se neztratí
✅ Auto-refresh se automaticky obnoví po ukončení plánování
✅ Uživatel může pokračovat v plánování bez přerušení
✅ Manuální refresh (F5/Ctrl+R) funguje vždy

## Chování
- **Před plánováním**: Auto-refresh běží normálně každých 30s
- **Během plánování**: Auto-refresh pozastaven, zobrazuje se zpráva pozastavení
- **Po ukončení**: Auto-refresh se obnoví automaticky

Status: ✅ VYŘEŠENO

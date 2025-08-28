# Oprava TypeError při načítání rezervací

## Problém
TypeError při načítání rezervací po uložení plánování ordinačních časů:
```
TypeError: 'NoneType' object is not subscriptable
```

## Příčina
Funkce `get_doktor_isactive_by_color()` vracela `None` když nenašla doktora s danou barvou, ale kód se pokouší přistoupit k `row[0]` bez kontroly.

## Řešení

### 1. Oprava NULL kontroly (`models/doktori.py`)
```python
def get_doktor_isactive_by_color(barva):
    # PŘED
    return row[0]
    
    # PO
    return row[0] if row else None
```

### 2. Bezpečné zpracování v hlavním okně (`views/hlavni_okno.py`)
```python
# PŘED
if get_doktor_isactive_by_color(r[2]) == 1:

# PO  
doktor_active = get_doktor_isactive_by_color(r[2])
if doktor_active == 1:
```

## Výsledek
✅ Aplikace nepadá při načítání rezervací
✅ Bezpečné zpracování chybějících doktorů podle barvy
✅ Plánování ordinačních časů funguje bez chyb

## Souvislost
Tato chyba se objevila při načítání rezervací po uložení plánování ordinačních časů, pravděpodobně kvůli nekonzistentním barvám doktorů v databázi.

Status: ✅ VYŘEŠENO

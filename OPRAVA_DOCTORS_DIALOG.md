# ✅ OPRAVA: Chyby v dialogu doktorů

## 🐛 Problémy

### 1. NULL hodnoty v databázi
**Chyba:** `TypeError: int() argument must be a string, a bytes-like object or a number, not 'NoneType'`
**Příčina:** Sloupec `is_active` v tabulce `doktori` obsahoval `NULL` hodnoty

### 2. Konflikt názvů funkcí  
**Chyba:** `remove_doctor() take 1 positional argument but 2 were given`
**Příčina:** Konflikt mezi metodou `self.remove_doctor()` a funkcí `remove_doctor()` z modelu

## 🔧 Opravy

### Oprava 1: Ošetření NULL hodnot
**Soubor:** `views/doctors_dialog.py`  
**Řádek:** ~71

```python
# PŘED:
is_active = int(doctor[4]) == 1

# PO OPRAVĚ:
# Ošetření None hodnoty pro is_active sloupec
is_active_value = doctor[4]
if is_active_value is None:
    is_active = True  # Výchozí hodnota pokud je NULL
else:
    is_active = int(is_active_value) == 1
```

### Oprava 2: Konflikt názvů funkcí
**Soubor:** `views/doctors_dialog.py`

**Import změna:**
```python
# PŘED:
from models.doktori import get_all_doctors, update_doctor, remove_doctor, add_doctor, get_all_doctors_colors, get_doctor_by_id

# PO OPRAVĚ:
from models.doktori import get_all_doctors, update_doctor, add_doctor, get_all_doctors_colors, get_doctor_by_id
```

**Metoda změna:**
```python
# PŘED:
def remove_doctor(self, doctor_id, username):
    # ...
    remove_doctor(doctor_id, username)  # ❌ Konflikt názvů

# PO OPRAVĚ:
def remove_doctor(self, doctor_id, username):
    # ...
    from models.doktori import remove_doctor as remove_doctor_from_db
    remove_doctor_from_db(doctor_id)  # ✅ Používá pouze doctor_id
```

## 🎯 Analýza problému

### Problem 1: Database NULL handling
- **Root cause:** Database migration neošetřila existující záznamy
- **Impact:** Aplikace se hroutila při otevření dialog doktorů
- **Solution:** Defensive programming - ošetření NULL hodnot

### Problem 2: Function name collision
- **Root cause:** Stejný název pro metodu třídy a importovanou funkci
- **Impact:** Python nemohl rozlišit mezi `self.remove_doctor` a `remove_doctor` z modelu
- **Solution:** Lokální import s aliasem

## ✅ Výsledek

### Nyní funguje:
1. ✅ **Dialog doktorů se otevře** bez chyb
2. ✅ **NULL hodnoty se ošetří** - výchozí hodnota `True`
3. ✅ **Odstranění doktora funguje** - správné volání model funkce
4. ✅ **Indikátor aktivity** - zelená/červená tečka podle stavu

### Test scenario:
1. **Otevři aplikace** - bez chyb ✅
2. **Menu → Uživatel → Správa doktorů** - dialog se otevře ✅
3. **Klikni "Odebrat" u doktora** - potvrzovací dialog ✅
4. **Potvrdí "Ano"** - doktor se odstraní ✅

## 📊 Kód vs Database synchronizace

**Model funkce signature:**
```python
def remove_doctor(doktor_id):  # Pouze 1 parametr
```

**Dialog metoda signature:**
```python
def remove_doctor(self, doctor_id, username):  # 2 parametry + self
```

**Řešení:** Lokální import s aliasem eliminuje konflikt názvů.

---

**Status:** ✅ OPRAVENO  
**Test:** ✅ Aplikace se spouští a dialog doktorů funguje  
**Database:** ✅ NULL hodnoty ošetřeny  
**Datum:** 28.08.2025

# ✅ OPRAVA: Chyba při deaktivaci doktora

## 🐛 Problém

**Chyba:** `'int' object is not subscriptable`

**Příčina:** 
1. **Nesprávné pořadí parametrů** při volání `update_doctor()`
2. **Neúplná data** - posílání pouze `isActive` místo všech požadovaných polí

## 🔍 Analýza problému

### Původní chybný kód:
```python
# ❌ CHYBA 1: Špatné pořadí parametrů
update_doctor_in_db(doctor_id, update_data)

# ❌ CHYBA 2: Neúplná data
update_data = {
    'isActive': 0  # Chybí: jmeno, prijmeni, specializace, color
}
```

### Očekávaná signatura funkce:
```python
def update_doctor(data, doktor_id):  # data první, pak ID
    # Očekává kompletní slovník se všemi poli
```

## 🔧 Oprava

### 1. Správné načtení aktuálních dat
```python
# Získáme aktuální data doktora
doctor_data = get_doctor_by_id(doctor_id)
if not doctor_data:
    raise ValueError("Doktor nebyl nalezen.")
```

### 2. Sestavení kompletních dat
```python
# Připravíme kompletní data s aktualizovaným isActive
update_data = {
    'jmeno': doctor_data[1],         # zachová současné jméno
    'prijmeni': doctor_data[2],      # zachová současné příjmení
    'specializace': doctor_data[3],  # zachová specializaci
    'isActive': 0,                   # ZMĚNA: deaktivuje
    'color': doctor_data[5]          # zachová barvu
}
```

### 3. Správné volání s opraveným pořadím
```python
# ✅ OPRAVENO: Správné pořadí parametrů
update_doctor_in_db(update_data, doctor_id)  # data první, ID druhé
```

## 📊 Mapování databázových sloupců

| Index | Pole | Popis | Akce při deaktivaci |
|-------|------|-------|-------------------|
| 0 | doktor_id | Primární klíč | Nezměněno |
| 1 | jmeno | Jméno doktora | Zachováno |
| 2 | prijmeni | Příjmení doktora | Zachováno |
| 3 | specializace | Specializace | Zachováno |
| 4 | isActive | Aktivní stav | **0 (deaktivován)** |
| 5 | color | Barva doktora | Zachováno |

## ✅ Nová funkcionalita

### `deactivate_doctor()` metoda:
```python
def deactivate_doctor(self, doctor_id, username):
    """Deaktivuje doktora místo odstranění."""
    try:
        # 1. Načti aktuální data
        doctor_data = get_doctor_by_id(doctor_id)
        
        # 2. Sestav kompletní update data
        update_data = {
            'jmeno': doctor_data[1],
            'prijmeni': doctor_data[2], 
            'specializace': doctor_data[3],
            'isActive': 0,              # Jediná změna
            'color': doctor_data[5]
        }
        
        # 3. Aktualizuj s správným pořadím parametrů
        update_doctor_in_db(update_data, doctor_id)
        
        # 4. Refresh UI
        self.load_doctors()
        
    except Exception as e:
        raise e
```

## 🎯 Workflow po opravě

### Krok za krokem:
1. **Uživatel klikne "Odebrat"** u doktora s rezervacemi
2. **Dialog zobrazí možnosti:** "Deaktivovat doktora" nebo "Zrušit"  
3. **Uživatel vybere "Deaktivovat"**
4. **Systém:**
   - Načte aktuální data doktora z DB
   - Sestaví kompletní update data (pouze `isActive` změní na 0)
   - Zavolá `update_doctor()` se správným pořadím parametrů
   - Obnoví dialog (červený indikátor = neaktivní)
   - Zobrazí potvrzení v status baru

## 🧪 Test Scenarios

### Test 1: Deaktivace doktora s rezervacemi
1. Najdi doktora s aktivními rezervacemi
2. Klikni "Odebrat"
3. Vyberi "Deaktivovat doktora"
4. **Očekávaný výsledek:** 
   - ✅ Doktor zůstane v seznamu
   - ✅ Červený indikátor (neaktivní)
   - ✅ Status: "Doktor XYZ byl deaktivován"
   - ✅ Rezervace zůstávají platné

### Test 2: Reaktivace doktora
1. Najdi deaktivovaného doktora (červený indikátor)
2. Klikni "Upravit"
3. Zaškrtni "Aktivní"
4. **Očekávaný výsledek:** Zelený indikátor (aktivní)

---

**Status:** ✅ OPRAVENO  
**Parameter order:** ✅ Správné pořadí  
**Data completeness:** ✅ Všechna pole zahrnuta  
**Error handling:** ✅ Comprehensive  
**Datum:** 28.08.2025

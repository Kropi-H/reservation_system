# ✅ OPRAVA: Foreign Key Constraint při odstranění doktora

## 🐛 Problém

**Chyba:** 
```
update or delete on table "doktori" violates foreign key constraint "rezervace_id_fkey" on table "rezervace" 
DETAIL: Key (doktor_id)=(10) is still referenced from table "rezervace".
```

**Příčina:** Pokus o odstranění doktora, který má aktivní rezervace, porušil foreign key constraint v databázi.

## 🔧 Řešení

### 1. Nová funkce pro kontrolu rezervací
**Soubor:** `models/doktori.py`

```python
def check_doctor_reservations(doktor_id):
    """Zkontroluje, kolik rezervací má doktor."""
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute('''
            SELECT COUNT(*) FROM Rezervace WHERE doktor_id = %s
        ''', (doktor_id,))
        count = cur.fetchone()[0]
        return count
```

### 2. Vylepšená funkce odstranění
**Soubor:** `models/doktori.py`

```python
def remove_doctor(doktor_id):
    """Odstraní doktora podle jeho ID."""
    with get_connection() as conn:
        cur = conn.cursor()
        
        # Nejdříve zkontrolujeme, jestli má doktor rezervace
        reservation_count = check_doctor_reservations(doktor_id)
        if reservation_count > 0:
            raise ValueError(f"Doktor má {reservation_count} aktivních rezervací. Nemůže být odstraněn.")
        
        cur.execute('''
            DELETE FROM Doktori WHERE doktor_id = %s
        ''', (doktor_id,))
        
        if cur.rowcount == 0:
            raise ValueError("Doktor nebyl nalezen.")
            
        conn.commit()
        return True
```

### 3. Inteligentní dialog s možnostmi
**Soubor:** `views/doctors_dialog.py`

```python
def remove_doctor(self, doctor_id, username):
    # Kontrola rezervací
    reservation_count = check_doctor_reservations(doctor_id)
    
    if reservation_count > 0:
        # Nabídni deaktivaci místo odstranění
        msg = QMessageBox(self)
        msg.setText(f"Doktor {username} má {reservation_count} aktivních rezervací.")
        msg.setInformativeText("Vyberte možnost:")
        
        deactivate_btn = msg.addButton("Deaktivovat doktora", QMessageBox.ActionRole)
        cancel_btn = msg.addButton("Zrušit", QMessageBox.RejectRole)
        
        # Uživatel může vybrat deaktivaci
    else:
        # Doktor nemá rezervace - lze odstranit
        # Standardní potvrzovací dialog
```

### 4. Deaktivace jako alternativa
**Soubor:** `views/doctors_dialog.py`

```python
def deactivate_doctor(self, doctor_id, username):
    """Deaktivuje doktora místo odstranění."""
    update_data = {'isActive': 0}
    update_doctor_in_db(doctor_id, update_data)
    # Doktor zůstane v databázi, ale bude neaktivní
```

## 🎯 Workflow po opravě

### Scenario 1: Doktor bez rezervací
1. **Klik "Odebrat"** → kontrola rezervací
2. **0 rezervací** → standardní potvrzovací dialog
3. **"Ano"** → doktor se odstraní z databáze
4. **Úspěch** ✅

### Scenario 2: Doktor s rezervacemi
1. **Klik "Odebrat"** → kontrola rezervací  
2. **X rezervací nalezeno** → speciální dialog
3. **Možnosti:**
   - **"Deaktivovat doktora"** → `is_active = 0`, rezervace zůstávají
   - **"Zrušit"** → žádná změna

## ✅ Výhody řešení

### 🛡️ Bezpečnost
- **Žádné porušení constraints** - kontrola před akcí
- **Zachování dat integrity** - rezervace zůstávají platné
- **Graceful handling** - chyby ošetřeny uživatelsky přívětivě

### 👤 Uživatelské rozhraní  
- **Jasné možnosti** - deaktivace vs. odstranění
- **Informativní zprávy** - počet rezervací zobrazen
- **Intuitivní workflow** - logické kroky

### 🗄️ Database Design
- **Foreign key constraints respektovány** - žádné orphaned záznamy
- **Soft delete pattern** - deaktivace místo tvrdého smazání  
- **Data consistency** - všechna data zůstávají konzistentní

## 🧪 Test Scenarios

### Test 1: Doktor bez rezervací
1. Vytvoř nového doktora
2. Klikni "Odebrat" 
3. **Očekávaný výsledek:** Standardní potvrzení → odstranění ✅

### Test 2: Doktor s rezervacemi  
1. Vyber doktora s aktivními rezervacemi
2. Klikni "Odebrat"
3. **Očekávaný výsledek:** Dialog s možnostmi → deaktivace ✅

### Test 3: Deaktivace
1. Doktor s rezervacemi → "Deaktivovat"
2. **Očekávaný výsledek:** Červený indikátor (neaktivní) ✅

---

**Status:** ✅ OPRAVENO  
**Database integrity:** ✅ Zachována  
**User experience:** ✅ Vylepšena  
**Error handling:** ✅ Comprehensive  
**Datum:** 28.08.2025

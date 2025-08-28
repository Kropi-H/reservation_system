# 🔧 DEBUG: Problém s ordinačním časem doktora

## 🐛 Chyba

**Error:** `ValueError: Doktor nebo ordinace nenalezena.`

**Místo:** `uloz_nebo_uprav_ordinacni_cas()` v `models/doktori.py`

## 🔍 Debugging zapnuto

Přidal jsem debug výstupy do funkce `uloz_nebo_uprav_ordinacni_cas()`:

```python
print(f"🔍 DEBUG: Hledám doktora: '{novy_doktor}'")
print(f"🔍 DEBUG: Hledám ordinaci: '{nazev_ordinace}'")
print(f"🔍 DEBUG: Doktor ID: {novy_doktor_id}")
print(f"🔍 DEBUG: Ordinace ID: {ordinace_id}")

# Plus výpis všech dostupných doktorů a ordinací
```

## 🎯 Jak reprodukovat chybu pro debugging:

1. **Spusť aplikaci:** `python main.py`
2. **Přihlas se jako admin**
3. **Menu → Uživatel → Plánování ordinací**
4. **Vyber doktora a časy**
5. **Klikni "Uložit vybraný čas"**
6. **Sleduj console výstup** - ukáže co se hledá vs. co je dostupné

## 🔍 Možné příčiny:

### 1. Problém s názvem doktora
```python
# Funkce očekává: "Jméno Příjmení"
# Ale možná dostává: "Dr. Jméno Příjmení" nebo jiný formát
```

### 2. Problém s názvem ordinace  
```python
# Funkce očekává: "Ordinace 1"
# Ale možná dostává: "ordinace 1" (malé písmeno) nebo jiný formát
```

### 3. Neaktivní doktori
```python
# Možná se hledá neaktivní doktor (is_active = 0)
# Ale get_doktor_id() hledá ve všech doktorech
```

## 🔧 Možná řešení:

### Řešení 1: Case-insensitive search
```python
def get_doktor_id(doktor):
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute('''
            SELECT doktor_id FROM Doktori
            WHERE LOWER(jmeno) = LOWER(%s) AND LOWER(prijmeni) = LOWER(%s)
        ''', (
             doktor.split()[0],
             doktor.split(maxsplit=1)[1] if len(doktor.split()) > 1 else "",
        ))
        row = cur.fetchone()
        return row[0] if row else None
```

### Řešení 2: Trim whitespace
```python
def get_ordinace_id(nazev):
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute('''
            SELECT ordinace_id FROM Ordinace
            WHERE TRIM(nazev) = TRIM(%s)
        ''', (nazev.strip(),))
        row = cur.fetchone()
        return row[0] if row else None
```

### Řešení 3: Fuzzy matching
```python
def get_doktor_id_fuzzy(doktor):
    # Pokud přesné hledání selže, zkus fuzzy match
    parts = doktor.split()
    if len(parts) >= 2:
        jmeno = parts[0]
        prijmeni = parts[-1]  # Poslední část jako příjmení
        
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute('''
                SELECT doktor_id FROM Doktori
                WHERE jmeno ILIKE %s AND prijmeni ILIKE %s
            ''', (f'%{jmeno}%', f'%{prijmeni}%'))
            row = cur.fetchone()
            return row[0] if row else None
    return None
```

## 📝 Akční plán:

1. **Reprodukuj chybu** s debug výstupem
2. **Analyzuj** co se hledá vs. co je v databázi
3. **Implementuj** vhodné řešení podle root cause
4. **Otestuj** opravený kód
5. **Odstraň** debug výstupy

---

**Status:** 🔄 Debugging probíhá  
**Next:** Reprodukuj chybu s debug výstupem  
**Goal:** Identifikovat přesnou příčinu a opravit

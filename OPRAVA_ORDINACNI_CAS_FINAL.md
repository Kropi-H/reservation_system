# Oprava plánování ordinačních časů - FINÁLNÍ

## Problém
ValueError při ukládání ordinačních časů doktorů: "Doktor 'Zuzana  Bošková' nebo ordinace 'Ordinace 1' nenalezena."

## Příčina
1. **Whitespace normalizace**: Jména doktorů obsahovala nekonzistentní mezery (např. 'Zuzana  Bošková' s dvojitou mezerou)
2. **SQL syntax chyby**: Mícháním SQLite (`?`) a PostgreSQL (`%s`) placeholders

## Řešení

### 1. Oprava vyhledávání doktorů (`models/doktori.py`)
```python
def get_doktor_id(doktor):
    # Normalize whitespace - remove extra spaces
    doktor_normalized = ' '.join(doktor.split())
    
    # První pokus - přímé vyhledávání
    # Pokud nenajde, fuzzy search s normalizací databázových jmen
    if not row:
        cur.execute('SELECT doktor_id, jmeno, prijmeni FROM Doktori')
        all_doctors = cur.fetchall()
        
        for doc_id, jmeno, prijmeni in all_doctors:
            db_name_normalized = ' '.join(f"{jmeno} {prijmeni}".split())
            if db_name_normalized.lower() == doktor_normalized.lower():
                return doc_id
```

### 2. Normalizace vstupů (`uloz_nebo_uprav_ordinacni_cas`)
```python
# Normalize inputs - remove extra whitespace
novy_doktor_normalized = ' '.join(novy_doktor.split())
nazev_ordinace_normalized = nazev_ordinace.strip()
```

### 3. Oprava SQL placeholders
Změna všech `?` na `%s` pro PostgreSQL kompatibilitu:
```python
# PŘED
cur.execute('UPDATE Doktori_Ordinacni_Cas SET prace_od = ? WHERE work_id = %s', ...)

# PO  
cur.execute('UPDATE Doktori_Ordinacni_Cas SET prace_od = %s WHERE work_id = %s', ...)
```

## Výsledek
✅ Plánování doktorů funguje bez chyb
✅ Fuzzy matching pro nekonzistentní whitespace
✅ PostgreSQL kompatibilní SQL dotazy
✅ Debug výstupy odstraněny

## Testováno
- Úspěšné ukládání časů pro 'Zuzana  Bošková' (s dvojitou mezerou)
- Normalizace na 'Zuzana Bošková' (s jednoduchou mezerou)
- Správné nalezení doktor_id = 10
- Všechny SQL operace bez TypeError

Status: ✅ VYŘEŠENO

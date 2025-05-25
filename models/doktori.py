from models.databaze import get_connection

def get_doktor_id(doktor):
    """Vrátí doktor_id podle jména a příjmení."""
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute('''
            SELECT doktor_id FROM Doktori
            WHERE jmeno = ? AND prijmeni = ?
        ''', (
             doktor.split()[0],
             doktor.split(maxsplit=1)[1] if len(doktor.split()) > 1 else "",
              ))
        row = cur.fetchone()
        return row[0] if row else None

def get_ordinace_id(nazev):
    """Vrátí ordinace_id podle názvu ordinace."""
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute('''
            SELECT ordinace_id FROM Ordinace
            WHERE nazev = ?
        ''', (nazev,))
        row = cur.fetchone()
        return row[0] if row else None

def vloz_ordinacni_cas(doktor, datum, prace_od, prace_do, nazev_ordinace):
    """Vloží záznam do Doktori_Ordinacni_Cas podle jména doktora a názvu ordinace."""
    doktor_id = get_doktor_id(doktor)
    ordinace_id = get_ordinace_id(nazev_ordinace)
    if doktor_id is None or ordinace_id is None:
        raise ValueError("Doktor nebo ordinace nenalezena.")
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute('''
            INSERT INTO Doktori_Ordinacni_Cas (doktor_id, datum, prace_od, prace_do, ordinace_id)
            VALUES (?, ?, ?, ?, ?)
        ''', (doktor_id, datum, prace_od, prace_do, ordinace_id))
        conn.commit()
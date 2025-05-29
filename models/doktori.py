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
      
def get_doctor_work_times(doktor_id):
    """Vrátí pracovní časy doktora."""
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute('''
        SELECT datum, prace_od, prace_do, ordinace_id
        FROM Doktori_Ordinacni_Cas
        WHERE doktor_id = ?
        ''', (doktor_id,))
        return cur.fetchall()

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
        
def ziskej_rozvrh_doktoru_dne(den_v_tydnu):
    """
    Vrátí seznam doktorů a jejich barvy pro daný den v týdnu.
    Datum ve formátu 2025-05-19 08:00
    Výstup: [(doktor_id, 'Jméno Příjmení', 'Barva', datum, prace_od, prace_do, nazev_ordinace), ...]
    """
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute('''
        SELECT 
            Doktori.doktor_id,
            Doktori.jmeno || ' ' || Doktori.prijmeni AS Doktor,
            Doktori.color AS Barva,
            Doktori_Ordinacni_Cas.datum,
            Doktori_Ordinacni_Cas.prace_od,
            Doktori_Ordinacni_Cas.prace_do,
            Ordinace.nazev AS Ordinace
        FROM Doktori_Ordinacni_Cas
        INNER JOIN Doktori ON Doktori_Ordinacni_Cas.doktor_id = Doktori.doktor_id
        INNER JOIN Ordinace ON Doktori_Ordinacni_Cas.ordinace_id = Ordinace.ordinace_id
        WHERE Doktori_Ordinacni_Cas.datum = ?
        ORDER BY Doktori_Ordinacni_Cas.prace_od
        ''', (den_v_tydnu,))
        return cur.fetchall()
from models.databaze import get_connection, get_or_create

def pridej_rezervaci(pacient_jmeno, pacient_druh, majitel_pacienta, majitel_kontakt, doktor, note, cas, mistnost):
    """
    Přidá novou rezervaci.
    """
    with get_connection() as conn:
        cur = conn.cursor()

        # 1) Doktor
        doc_id = get_or_create(
            cur,
            table="Doktori",
            unique_cols=("jmeno","prijmeni"),
            data_cols={
                "jmeno": doktor.split()[0],
                "prijmeni": doktor.split(maxsplit=1)[1] if len(doktor.split()) > 1 else "",
            }
        )

        # 2) Pacient (zvíře + majitel)
        pac_id = get_or_create(
            cur,
            table="Pacienti",
            unique_cols=("jmeno_zvirete","druh","majitel_jmeno","majitel_telefon", "poznamka"),
            data_cols={
                "jmeno_zvirete": pacient_jmeno,
                "druh":          pacient_druh,
                "majitel_jmeno": majitel_pacienta,
                "majitel_telefon": majitel_kontakt,
                "poznamka": note
            }
        )

        # 3) Ordinace
        ord_id = get_or_create(
            cur,
            table="Ordinace",
            unique_cols=("nazev",),
            data_cols={"nazev": mistnost}
        )

        # 4) Vložíme rezervaci
        cur.execute(
            """
            INSERT INTO Rezervace
            (pacient_id, doktor_id, ordinace_id, termin)
            VALUES (?, ?, ?, ?)
            """,
            (pac_id, doc_id, ord_id, cas)
        )

        return cur.lastrowid  # id nově vzniklé rezervace

def aktualizuj_rezervaci(rezervace_id, pacient_jmeno, pacient_druh, majitel_pacienta, majitel_kontakt, doktor, note, cas, mistnost):
    """
    Aktualizuje existující rezervaci podle rezervace_id.
    """
    with get_connection() as conn:
        cur = conn.cursor()

        # 1) Doktor
        doc_id = get_or_create(
            cur,
            table="Doktori",
            unique_cols=("jmeno","prijmeni"),
            data_cols={
                "jmeno": doktor.split()[0],
                "prijmeni": doktor.split(maxsplit=1)[1] if len(doktor.split()) > 1 else "",
            }
        )

        # 2) Pacient (zvíře + majitel)
        pac_id = get_or_create(
            cur,
            table="Pacienti",
            unique_cols=("jmeno_zvirete","druh","majitel_jmeno","majitel_telefon", "poznamka"),
            data_cols={
                "jmeno_zvirete": pacient_jmeno,
                "druh":          pacient_druh,
                "majitel_jmeno": majitel_pacienta,
                "majitel_telefon": majitel_kontakt,
                "poznamka": note
            }
        )

        # 3) Ordinace
        ord_id = get_or_create(
            cur,
            table="Ordinace",
            unique_cols=("nazev",),
            data_cols={"nazev": mistnost}
        )

        # 4) Aktualizace rezervace
        cur.execute(
            """
            UPDATE Rezervace
            SET pacient_id = ?, doktor_id = ?, ordinace_id = ?, termin = ?
            WHERE rezervace_id = ?
            """,
            (pac_id, doc_id, ord_id, cas, rezervace_id)
        )

        return cur.rowcount > 0  # True pokud byl záznam upraven

def rezervace_pro_ordinaci(ordinace_id):
    """
    Vrátí seznam rezervací pro danou ordinaci.
    """
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute('''
        SELECT 
            Rezervace.rezervace_id AS id,
            Rezervace.termin AS Cas,
            Ordinace.nazev AS Ordinace
        FROM Rezervace
        INNER JOIN Ordinace ON Rezervace.ordinace_id = Ordinace.ordinace_id
        WHERE Rezervace.ordinace_id = ?
        ORDER BY Rezervace.termin
        ''', (ordinace_id,))
        return cur.fetchall()

def ziskej_rezervace_dne(datum_str):
    """
    Vrátí seznam rezervací pro daný den (datum ve formátu 'YYYY-MM-DD') s detaily:
    "Čas", "Rezervace ID", "Doktor", "Barva", "Pacient", "Majitel", "Kontakt", "Druh", "Ordinace", "Poznámka".
    """
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute('''
        SELECT 
            Rezervace.termin AS Cas,
            Rezervace.rezervace_id AS id,
            Doktori.jmeno || ' ' || Doktori.prijmeni AS Doktor,
            Doktori.color AS Barva,
            Pacienti.jmeno_zvirete AS Pacient,
            Pacienti.majitel_jmeno AS Majitel,
            Pacienti.majitel_telefon AS Kontakt,
            Pacienti.druh AS Druh,
            Ordinace.nazev AS Ordinace,
            Pacienti.poznamka AS Poznamka
        FROM Rezervace
        INNER JOIN Doktori ON Rezervace.doktor_id = Doktori.doktor_id
        INNER JOIN Pacienti ON Rezervace.pacient_id = Pacienti.pacient_id
        INNER JOIN Ordinace ON Rezervace.ordinace_id = Ordinace.ordinace_id
        WHERE DATE(Rezervace.termin) = ?
        ORDER BY Rezervace.termin
        ''', (datum_str,))
        return cur.fetchall()

def odstran_rezervaci(rezervace_id):
    """
    Odstraní rezervaci podle rezervace_id.
    """
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute('''
        DELETE FROM Rezervace
        WHERE rezervace_id = ?
        ''', (rezervace_id,))
        return cur.rowcount > 0  # True pokud byl záznam odstraněn
      
def remove_all_older_rezervations_for_ordinaci(ordinace_id):
    """
    Odstraní všechny rezervace pro danou ordinaci, které jsou starší než aktuální čas.
    """
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute('''
        DELETE FROM Rezervace
        WHERE ordinace_id = ? 
        ''', (ordinace_id,))
        return cur.rowcount > 0  # True pokud byly záznamy odstraněny
    

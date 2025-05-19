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

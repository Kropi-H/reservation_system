from models.databaze import get_connection, get_or_create
from datetime import datetime, timedelta

# Import pro database notifikace (pouze pokud je dostupný)
try:
    from models.database_listener import notify_database_change
    NOTIFICATIONS_ENABLED = True
except ImportError:
    NOTIFICATIONS_ENABLED = False
    def notify_database_change(*args, **kwargs):
        pass  # No-op pokud není dostupný

def pridej_rezervaci(pacient_problem, pacient_druh, majitel_pacienta, majitel_kontakt, doktor, anestezie, druhy_doktor, note, termin, cas_od, cas_do, mistnost):
    """
    Přidá novou rezervaci.
    """
    with get_connection() as conn:
        cur = conn.cursor()

        # 1) Doktor
        doc_id = None
        if doktor and doktor != "!---Vyberte doktora---!":
          doc_id = get_or_create(
              cur,
              table="Doktori",
              unique_cols=("jmeno","prijmeni"),
              data_cols={
                  "jmeno": doktor.split()[0],
                  "prijmeni": doktor.split(maxsplit=1)[1] if len(doktor.split()) > 1 else "",
              }
          )
        
        # 2) Druhý doktor (pokud je vybrán)
        druhy_doc_id = None
        if druhy_doktor and druhy_doktor != "!---Vyberte druhého doktora---!":
            druhy_doc_id = get_or_create(
                cur,
                table="Doktori",
                unique_cols=("jmeno","prijmeni"),
                data_cols={
                    "jmeno": druhy_doktor.split()[0],
                    "prijmeni": druhy_doktor.split(maxsplit=1)[1] if len(druhy_doktor.split()) > 1 else "",
                }
            )

        # 3) Pacient (zvíře + majitel)
        pac_id = get_or_create(
            cur,
            table="Pacienti",
            unique_cols=("pacient_problem","druh","majitel_jmeno","majitel_telefon", "poznamka"),
            data_cols={
                "pacient_problem": pacient_problem,
                "druh":          pacient_druh,
                "majitel_jmeno": majitel_pacienta,
                "majitel_telefon": majitel_kontakt,
                "poznamka": note
            }
        )

        # 4) Ordinace
        ord_id = get_or_create(
            cur,
            table="Ordinace",
            unique_cols=("nazev",),
            data_cols={"nazev": mistnost}
        )

        # 5) Vložíme rezervaci s novými sloupci
        cur.execute(
            """
            INSERT INTO Rezervace
            (pacient_id, doktor_id, druhy_doktor_id, ordinace_id, termin, cas_od, cas_do, anestezie)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING rezervace_id
            """,
            (pac_id, doc_id, druhy_doc_id, ord_id, termin, cas_od, cas_do, anestezie)
        )

        result = cur.fetchone()
        rezervace_id = result[0] if result else None
        
        # Pošli notifikaci o nové rezervaci
        if rezervace_id and NOTIFICATIONS_ENABLED:
            notify_database_change('reservation', 'INSERT', {
                'id': rezervace_id,
                'pacient_problem': pacient_problem,
                'majitel_pacienta': majitel_pacienta,
                'doktor': doktor,
                'druhy_doktor': druhy_doktor,
                'anestezie': anestezie,
                'termin': str(termin),
                'cas_od': str(cas_od),
                'cas_do': str(cas_do),
                'mistnost': mistnost
            })
        
        return rezervace_id  # id nově vzniklé rezervace

def aktualizuj_rezervaci(rezervace_id, pacient_problem, pacient_druh, majitel_pacienta, majitel_kontakt, doktor, anestezie, druhy_doktor, note, termin, cas_od, cas_do, mistnost):
    """
    Aktualizuje existující rezervaci podle rezervace_id.
    """
    with get_connection() as conn:
        cur = conn.cursor()

        # Najdeme stávající pacient_id pro tuto rezervaci
        cur.execute('SELECT pacient_id FROM Rezervace WHERE rezervace_id = %s', (rezervace_id,))
        row = cur.fetchone()
        if not row:
            return False  # Rezervace neexistuje
        
        existing_pacient_id = row[0]

        # 1) Doktor
        doktor = doktor if doktor is not None else "None None"
        doc_id = get_or_create(
            cur,
            table="Doktori",
            unique_cols=("jmeno","prijmeni"),
            data_cols={
                "jmeno": doktor.split()[0],
                "prijmeni": doktor.split(maxsplit=1)[1] if len(doktor.split()) > 1 else "",
            }
        )

        # 2) Druhý doktor (pokud je vybrán)
        druhy_doc_id = None
        if druhy_doktor and druhy_doktor != "!---Vyberte druhého doktora---!":
            druhy_doc_id = get_or_create(
                cur,
                table="Doktori",
                unique_cols=("jmeno","prijmeni"),
                data_cols={
                    "jmeno": druhy_doktor.split()[0],
                    "prijmeni": druhy_doktor.split(maxsplit=1)[1] if len(druhy_doktor.split()) > 1 else "",
                }
            )

        # 3) Aktualizujeme existujícího pacienta místo vytváření nového
        cur.execute('''
            UPDATE Pacienti
            SET pacient_problem = %s, druh = %s, majitel_jmeno = %s, majitel_telefon = %s, poznamka = %s
            WHERE pacient_id = %s
        ''', (pacient_problem, pacient_druh, majitel_pacienta, majitel_kontakt, note, existing_pacient_id))

        # 4) Ordinace
        ord_id = get_or_create(
            cur,
            table="Ordinace",
            unique_cols=("nazev",),
            data_cols={"nazev": mistnost}
        )

        # 5) Aktualizace rezervace s novými sloupci
        cur.execute(
            """
            UPDATE Rezervace
            SET doktor_id = %s, druhy_doktor_id = %s, ordinace_id = %s, termin = %s, cas_od = %s, cas_do = %s, anestezie = %s
            WHERE rezervace_id = %s
            """,
            (doc_id, druhy_doc_id, ord_id, termin, cas_od, cas_do, anestezie, rezervace_id)
        )

        updated = cur.rowcount > 0
        
        # Pošli notifikaci o úpravě rezervace
        if updated and NOTIFICATIONS_ENABLED:
            notify_database_change('reservation', 'UPDATE', {
                'id': rezervace_id,
                'pacient_problem': pacient_problem,
                'majitel_pacienta': majitel_pacienta,
                'doktor': doktor,
                'druhy_doktor': druhy_doktor,
                'anestezie': anestezie,
                'termin': str(termin),
                'cas_od': str(cas_od),
                'cas_do': str(cas_do),
                'mistnost': mistnost
            })

        return updated # Vrátíme True pokud byla rezervace úspěšně aktualizována

def rezervace_pro_ordinaci(ordinace_id):
    """
    Vrátí seznam rezervací pro danou ordinaci.
    """
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute('''
        SELECT 
            Rezervace.rezervace_id AS id,
            Rezervace.termin AS Termin,
            Rezervace.cas_od AS Cas,
            Ordinace.nazev AS Ordinace
        FROM Rezervace
        INNER JOIN Ordinace ON Rezervace.ordinace_id = Ordinace.ordinace_id
        WHERE Rezervace.ordinace_id = %s
        ORDER BY Rezervace.termin
        ''', (ordinace_id,))
        result = cur.fetchall()
        print(f"Nalezené rezervace z databáze pro ordinaci ID: {ordinace_id}: {result}") 
        return result
      
def ziskej_rezervace_dne(datum_str):
    """
    Vrátí seznam rezervací pro daný den s novými sloupci anestezie a druhý doktor včetně barvy.
    """
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute('''
        SELECT 
            Rezervace.termin AS Termin,
            Rezervace.rezervace_id AS id,
            CASE 
                WHEN Doktori.jmeno IS NOT NULL AND Doktori.prijmeni IS NOT NULL
                THEN Doktori.jmeno || ' ' || Doktori.prijmeni
                ELSE NULL
            END AS Doktor,
            Doktori.color AS Barva,
            Pacienti.pacient_problem AS Pacient,
            Pacienti.majitel_jmeno AS Majitel,
            Pacienti.majitel_telefon AS Kontakt,
            Pacienti.druh AS Druh,
            Ordinace.nazev AS Ordinace,
            Pacienti.poznamka AS Poznamka,
            Rezervace.cas_od AS Cas_od,
            Rezervace.cas_do AS Cas_do,
            Rezervace.anestezie AS Anestezie,
            CASE 
                WHEN Rezervace.druhy_doktor_id IS NOT NULL 
                THEN DruhyDoktor.jmeno || ' ' || DruhyDoktor.prijmeni 
                ELSE NULL 
            END AS Druhy_doktor,
            CASE 
                WHEN Rezervace.druhy_doktor_id IS NOT NULL 
                THEN DruhyDoktor.color 
                ELSE NULL 
            END AS Druhy_doktor_barva,
            Rezervace.stav AS Stav
        FROM Rezervace
        LEFT JOIN Doktori ON Rezervace.doktor_id = Doktori.doktor_id
        LEFT JOIN Doktori AS DruhyDoktor ON Rezervace.druhy_doktor_id = DruhyDoktor.doktor_id
        INNER JOIN Pacienti ON Rezervace.pacient_id = Pacienti.pacient_id
        INNER JOIN Ordinace ON Rezervace.ordinace_id = Ordinace.ordinace_id
        WHERE Rezervace.termin = %s
        ORDER BY Rezervace.cas_od
        ''', (datum_str,))
        return cur.fetchall()

def odstran_rezervaci(rezervace_id):
    """
    Odstraní rezervaci podle rezervace_id.
    """
    with get_connection() as conn:
        cur = conn.cursor()
        # Zjistíme pacient_id pro tuto rezervaci
        cur.execute('SELECT pacient_id FROM Rezervace WHERE rezervace_id = %s', (rezervace_id,))
        row = cur.fetchone()
        if not row:
            return False  # Rezervace neexistuje
        pacient_id = row[0]
        
        cur.execute('''
        DELETE FROM Rezervace
        WHERE rezervace_id = %s
        ''', (rezervace_id,))
        deleted = cur.rowcount > 0  # True pokud byl záznam odstraněn
        
        # Pošli notifikaci o smazání rezervace
        if deleted and NOTIFICATIONS_ENABLED:
            notify_database_change('reservation', 'DELETE', {
                'id': rezervace_id
            })
        
        if deleted:
            # Zjistíme, zda má pacient ještě nějakou rezervaci
            cur.execute('SELECT COUNT(*) FROM Rezervace WHERE pacient_id = %s', (pacient_id,))
            count = cur.fetchone()[0]
            if count == 0:
                # Smažeme pacienta
                cur.execute('DELETE FROM Pacienti WHERE pacient_id = %s', (pacient_id,))
        conn.commit()
        return deleted  # Vrátíme True pokud byla rezervace úspěšně odstraněna
        
def remove_all_older_rezervations_for_ordinaci(ordinace_id):
    """
    Odstraní všechny rezervace pro danou ordinaci, které jsou starší než aktuální čas.
    """
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute('''
        DELETE FROM Rezervace
        WHERE ordinace_id = %s 
        ''', (ordinace_id,))
        return cur.rowcount > 0  # True pokud byly záznamy odstraněny
    
def smaz_rezervace_starsi_nez(pocet_dni):
    """
    Smaže rezervace a ordinační časy doktorů starší než zadaný počet dní od dneška.
    Pokud je pocet_dni = 0, nic se neudělá.
    
    Args:
        pocet_dni (int): Počet dní od dneška. Rezervace a ordinační časy starší budou smazány.
    
    Returns:
        dict: Slovník s počty smazaných rezervací a ordinačních časů
    """
    from models.doktori import smaz_ordinacni_casy_starsi_nez
    
    pocet_dni = int(pocet_dni)
    if pocet_dni <= 0:
        return {"pocet_smazanych_rezervaci": 0, "pocet_smazanych_ordinacnich_casu": 0, "datum_hranice": None}
    
    # Vypočítáme datum hranice
    datum_hranice = datetime.now() - timedelta(days=pocet_dni)
    datum_hranice_str = datum_hranice.strftime('%Y-%m-%d')
    
    with get_connection() as conn:
        cur = conn.cursor()
        
        # Najdeme pacienty, kteří budou mít smazané všechny rezervace
        cur.execute('''
        SELECT DISTINCT pacient_id 
        FROM Rezervace 
        WHERE DATE(termin) < %s
        ''', (datum_hranice_str,))
        
        pacienti_ke_smazani = [row[0] for row in cur.fetchall()]
        
        # Smažeme staré rezervace
        cur.execute('''
        DELETE FROM Rezervace 
        WHERE DATE(termin) < %s
        ''', (datum_hranice_str,))
        
        pocet_smazanych_rezervaci = cur.rowcount
        
        # Zkontrolujeme, kteří pacienti už nemají žádné rezervace
        for pacient_id in pacienti_ke_smazani:
            cur.execute('''
            SELECT COUNT(*) FROM Rezervace WHERE pacient_id = %s
            ''', (pacient_id,))
            
            if cur.fetchone()[0] == 0:
                # Pacient nemá žádné rezervace, smažeme ho
                cur.execute('DELETE FROM Pacienti WHERE pacient_id = %s', (pacient_id,))
        
        conn.commit()
    
    # Smažeme také staré ordinační časy doktorů
    result_ordinacni_casy = smaz_ordinacni_casy_starsi_nez(pocet_dni)
    
    return {
        "pocet_smazanych_rezervaci": pocet_smazanych_rezervaci,
        "pocet_smazanych_ordinacnich_casu": result_ordinacni_casy["pocet_smazanych"],
        "datum_hranice": datum_hranice_str
    }
      
def kontrola_prekryvani_rezervaci(termin, cas_od, cas_do, mistnost, rezervace_id=None):
    with get_connection() as conn:
        cur = conn.cursor()
        
        # Získáme ID ordinace
        cur.execute('SELECT ordinace_id FROM Ordinace WHERE nazev = %s', (mistnost,))
        result = cur.fetchone()
        if not result:
            return True, f"Ordinace '{mistnost}' neexistuje."
        
        ordinace_id = result[0]
        
        # Získáme všechny rezervace pro danou ordinaci a datum
        if rezervace_id:
            query = '''
                SELECT rezervace_id, cas_od, cas_do FROM Rezervace
                WHERE ordinace_id = %s AND termin = %s AND rezervace_id != %s
            '''
            params = (ordinace_id, termin, rezervace_id)
        else:
            query = '''
                SELECT rezervace_id, cas_od, cas_do FROM Rezervace
                WHERE ordinace_id = %s AND termin = %s
            '''
            params = (ordinace_id, termin)
        
        cur.execute(query, params)
        existujici_rezervace = cur.fetchall()

        
        try:
            novy_start = str_na_cas(cas_od)
            novy_konec = str_na_cas(cas_do)
            
            for rezervace in existujici_rezervace:
                existujici_start = str_na_cas(rezervace[1])
                existujici_konec = str_na_cas(rezervace[2])
                
                # Kontrola překrývání: dva časové úseky se nepřekrývají pouze pokud
                # jeden končí před začátkem druhého nebo začíná po konci druhého
                if novy_start <= existujici_konec and novy_konec >= existujici_start:
                    return True, f"Konflikt s jinou rezervací, vyberte jiný čas nebo ordinaci!"
            
            return False, ""
            
        except ValueError as e:
            return True, f"Chyba při parsování času: {e}"
          
def aktualizuj_stav_rezervace(rezervace_id, novy_stav):
    """
    Aktualizuje stav rezervace.
    
    Args:
        rezervace_id (int): ID rezervace
        novy_stav (str): Nový stav ('ceka', 'odbaven' nebo None)
    
    Returns:
        bool: True pokud byla aktualizace úspěšná
    """
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            "UPDATE Rezervace SET stav = %s WHERE rezervace_id = %s",
            (novy_stav, rezervace_id)
        )
        updated = cur.rowcount > 0
        
        # Pošli notifikaci o změně stavu
        if updated and NOTIFICATIONS_ENABLED:
            notify_database_change('reservation', 'UPDATE_STATUS', {
                'id': rezervace_id,
                'stav': novy_stav
            })
        
        return updated

# Pomocná funkce na převod řetězce na čas (bez data)
def str_na_cas(cas_str):
    return datetime.strptime(cas_str, "%H:%M").time()
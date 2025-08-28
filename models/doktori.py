from datetime import datetime, date
from models.databaze import get_connection


time_anchores = ["08:00","08:20", "08:40", "09:00", "09:15", "09:30", "09:45", "10:00", "10:20", "10:40",
                 "11:00", "11:20", "11:40", "12:00", "12:30", "12:40", "13:00", "13:20", "13:40", "14:00",
                 "14:20", "14:40", "15:00", "15:20", "15:40", "16:00", "16:15", "16:30", "16:45",
                 "17:20", "17:40", "18:00", "18:20", "18:40", "19:00", "19:20", "19:40", "20:00"]

def get_all_doctors():
    """Vrátí seznam všech doktorů a jejich barev."""
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute('''
            SELECT * FROM Doktori ORDER BY jmeno, prijmeni
        ''')
        return cur.fetchall()
        
def add_doctor(data):
    """Přidá nového doktora do databáze."""
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute('''
            INSERT INTO Doktori (jmeno, prijmeni, specializace, isActive, color)
            VALUES (%s, %s, %s, %s, %s)
        ''', (data["jmeno"], data["prijmeni"], data["specializace"], int(data["isActive"]), data["color"]))
        conn.commit()
        
def get_doctor_by_id(doktor_id):
    """Vrátí informace o doktorovi podle jeho ID."""
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute('''
            SELECT * FROM Doktori WHERE doktor_id = %s
        ''', (doktor_id,))
        row = cur.fetchone()
        return row if row else None
        
def update_doctor(data, doktor_id):
    """Aktualizuje informace o doktorovi."""
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute('''
            UPDATE Doktori
            SET jmeno = %s, prijmeni = %s, specializace = %s, isActive = %s, color = %s
            WHERE doktor_id = %s
        ''', (data["jmeno"], data["prijmeni"], data["specializace"], data["isActive"], data["color"], doktor_id))
        conn.commit()

def get_doktor_id(doktor):
    """Vrátí doktor_id podle jména a příjmení."""
    # Normalize whitespace - remove extra spaces
    doktor_normalized = ' '.join(doktor.split())
    
    with get_connection() as conn:
        cur = conn.cursor()
        # First try exact match with normalized input
        cur.execute('''
            SELECT doktor_id FROM Doktori
            WHERE jmeno = %s AND prijmeni = %s
        ''', (
             doktor_normalized.split()[0],
             doktor_normalized.split(maxsplit=1)[1] if len(doktor_normalized.split()) > 1 else "",
              ))
        row = cur.fetchone()
        
        # If not found, try fuzzy search by normalizing database values
        if not row:
            cur.execute('''
                SELECT doktor_id, jmeno, prijmeni FROM Doktori
            ''')
            all_doctors = cur.fetchall()
            
            for doc_id, jmeno, prijmeni in all_doctors:
                # Normalize database name the same way
                db_name_normalized = ' '.join(f"{jmeno} {prijmeni}".split())
                if db_name_normalized.lower() == doktor_normalized.lower():
                    return doc_id
        
        return row[0] if row else None

def get_doktor_isactive_by_color(barva):
    """Vrátí isActive status doktora podle barvy."""
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute('''
            SELECT isActive FROM Doktori WHERE color = %s
        ''', (barva,))
        row = cur.fetchone()
        return row[0] if row else None


def get_ordinace_id(nazev):
    """Vrátí ordinace_id podle názvu ordinace."""
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute('''
            SELECT ordinace_id FROM Ordinace
            WHERE nazev = %s
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
        WHERE doktor_id = %s
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
            VALUES (%s, %s, %s, %s, %s)
        ''', (doktor_id, datum, prace_od, prace_do, ordinace_id))
        conn.commit()

def get_doktor_jmeno_podle_barvy(barva):
    """Vrátí jméno a příjmení doktora podle barvy."""
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute('''
            SELECT doktor_id FROM Doktori WHERE color = %s
        ''', (barva,))
        row = cur.fetchone()
        if row:
            return f"{row[0]}"
        return None
      
def get_all_doctors_colors():
    """Vrátí seznam všech doktorů a jejich barev."""
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute('''
            SELECT color FROM Doktori
        ''')
        return cur.fetchall()
      
def get_doktor_color(doktor):
    """Vrátí doktor_id podle jména a příjmení."""
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute('''
            SELECT color FROM Doktori
            WHERE jmeno = %s AND prijmeni = %s
        ''', (
             doktor.split()[0],
             doktor.split(maxsplit=1)[1] if len(doktor.split()) > 1 else "",
              ))
        return cur.fetchone()


def uloz_nebo_uprav_ordinacni_cas(novy_doktor, barvy_puvodnich, datum, prace_od, prace_do, nazev_ordinace):
    """
    Přepíše úseky všech původních doktorů (dle seznamu barev) na nového doktora.
    Úseky původních doktorů, které se překrývají, se rozdělí/zkrátí/smažou.
    Nový úsek se vloží novému doktorovi a sloučí s navazujícími.
    """
    
    # Normalize inputs - remove extra whitespace
    novy_doktor_normalized = ' '.join(novy_doktor.split())
    nazev_ordinace_normalized = nazev_ordinace.strip()

    novy_doktor_id = get_doktor_id(novy_doktor_normalized)
    ordinace_id = get_ordinace_id(nazev_ordinace_normalized)
    
    if novy_doktor_id is None or ordinace_id is None:
        raise ValueError(f"Doktor '{novy_doktor}' nebo ordinace '{nazev_ordinace}' nenalezena.")

    # Ensure datum is properly formatted as string for PostgreSQL
    if isinstance(datum, date):
        datum_str = datum.strftime('%Y-%m-%d')
    else:
        datum_str = str(datum)

    prace_od_dt = datetime.strptime(prace_od, "%H:%M")
    prace_do_dt = datetime.strptime(prace_do, "%H:%M")
    # print(f"Nový záznam: {novy_doktor}, [{prace_od}, {prace_do}]")
    
    with get_connection() as conn:
        cur = conn.cursor()

        # 1. Uprav úseky všech původních doktorů podle barev
        if barvy_puvodnich:
            for barva in barvy_puvodnich:
              puvodni_doktor_id = get_doktor_jmeno_podle_barvy(barva)
              cur.execute('''
                  SELECT work_id, prace_od, prace_do FROM Doktori_Ordinacni_Cas
                  WHERE doktor_id = %s AND datum = %s AND ordinace_id = %s
              ''', (puvodni_doktor_id, datum_str, ordinace_id))
              rows = cur.fetchall()

              # print(f"původní záznam: {rows}")
              
              for zaznam_id, exist_od, exist_do in rows:
                  exist_od_dt = datetime.strptime(exist_od, "%H:%M")
                  exist_do_dt = datetime.strptime(exist_do, "%H:%M")

                  # Nový úsek zcela překrývá starý
                  if prace_od_dt <= exist_od_dt and prace_do_dt >= exist_do_dt:
                      # print("Nový úsek zcela překrývá starý")
                      cur.execute('DELETE FROM Doktori_Ordinacni_Cas WHERE work_id = %s', (zaznam_id,))
                      conn.commit()
                  # Nový úsek překrývá začátek starého
                  elif prace_od_dt <= exist_od_dt < prace_do_dt < exist_do_dt:
                      #print("Nový úsek překrývá začátek starého")
                      exist_do_dt = time_anchores[time_anchores.index(prace_do)+1]
                      cur.execute('UPDATE Doktori_Ordinacni_Cas SET prace_od = %s WHERE work_id = %s', (exist_do_dt, zaznam_id))
                      conn.commit()
                  # Nový úsek překrývá konec starého
                  elif exist_od_dt < prace_od_dt <= exist_do_dt <= prace_do_dt:
                      # print("Nový úsek překrývá konec starého")
                      exist_do_dt = time_anchores[time_anchores.index(exist_do)-1]
                      cur.execute('UPDATE Doktori_Ordinacni_Cas SET prace_do = %s WHERE work_id = %s', (exist_do_dt, zaznam_id))
                      conn.commit()
                  # Nový úsek je uvnitř starého (rozdělení na dva)
                  elif exist_od_dt < prace_od_dt and prace_do_dt < exist_do_dt:
                      # print("Nový úsek je uvnitř starého a rozdělí ho na dva")
                      exist_do_dt = time_anchores[time_anchores.index(prace_od)-1]
                      exist_new_od_dt = time_anchores[time_anchores.index(prace_od)+1]
                      cur.execute('UPDATE Doktori_Ordinacni_Cas SET prace_do = %s WHERE work_id = %s', (exist_do_dt, zaznam_id))
                      cur.execute('''
                          INSERT INTO Doktori_Ordinacni_Cas (doktor_id, datum, prace_od, prace_do, ordinace_id)
                          VALUES (%s, %s, %s, %s, %s)
                      ''', (puvodni_doktor_id, datum_str, exist_new_od_dt, exist_do, ordinace_id))
                      conn.commit()
                                    
                # 2. Přidej nový úsek novému doktorovi a slouč navazující
        cur.execute('''
            SELECT prace_od, prace_do FROM Doktori_Ordinacni_Cas
            WHERE doktor_id = %s AND datum = %s AND ordinace_id = %s
            ORDER BY prace_od
        ''', (novy_doktor_id, datum_str, ordinace_id))
        intervals = []
        for od, do in cur.fetchall():
            od_dt = datetime.strptime(od, "%H:%M")
            do_dt = datetime.strptime(do, "%H:%M")
            if od_dt > do_dt:
                od_dt, do_dt = do_dt, od_dt
            intervals.append((od_dt, do_dt))
        # Přidej nový úsek, vždy od menšího do většího
        if prace_od_dt > prace_do_dt:
            prace_od_dt, prace_do_dt = prace_do_dt, prace_od_dt
        intervals.append((prace_od_dt, prace_do_dt))
        intervals.sort()

        # Sluč navazující a překrývající se úseky podle time_anchores
        merged = []
        for start, end in intervals:
            if not merged:
                merged.append([start, end])
            else:
                last_start, last_end = merged[-1]
                last_end_str = last_end.strftime("%H:%M")
                start_str = start.strftime("%H:%M")
                try:
                    idx_last_end = time_anchores.index(last_end_str)
                    idx_start = time_anchores.index(start_str)
                except ValueError:
                    merged.append([start, end])
                    continue

                if idx_last_end >= idx_start or idx_last_end + 1 == idx_start:
                    merged[-1][1] = max(last_end, end)
                else:
                    merged.append([start, end])

        cur.execute('''
            DELETE FROM Doktori_Ordinacni_Cas
            WHERE doktor_id = %s AND datum = %s AND ordinace_id = %s
        ''', (novy_doktor_id, datum_str, ordinace_id))
        for od, do in merged:
            cur.execute('''
                INSERT INTO Doktori_Ordinacni_Cas (doktor_id, datum, prace_od, prace_do, ordinace_id)
                VALUES (%s, %s, %s, %s, %s)
            ''', (
                novy_doktor_id,
                datum_str,
                od.strftime("%H:%M"),
                do.strftime("%H:%M"),
                ordinace_id
            ))
        conn.commit()
        
def uprav_ordinacni_cas(barvy_puvodnich, datum, prace_od, prace_do, nazev_ordinace):
    # print(f"Upravování ordinacniho času pro doktora...: Barvy:{barvy_puvodnich}, Datum:{datum}, Prace od:{prace_od}, Prace do:{prace_do}, Ordinace:{nazev_ordinace} ")
    
    """Upraví ordinacni čas pro daného doktora."""
    ordinace_id = get_ordinace_id(nazev_ordinace)
    
    # Ensure datum is properly formatted as string for PostgreSQL
    if isinstance(datum, date):
        datum_str = datum.strftime('%Y-%m-%d')
    else:
        datum_str = str(datum)
        
    prace_od_dt = datetime.strptime(prace_od, "%H:%M")
    prace_do_dt = datetime.strptime(prace_do, "%H:%M")
    
    with get_connection() as conn:
        cur = conn.cursor()
    
        if barvy_puvodnich:
                for barva in barvy_puvodnich:
                  # print(f"Zpracovávám barvu: {barva}")
                  doktor_id = get_doktor_jmeno_podle_barvy(barva)
                  cur.execute('''
                      SELECT work_id, prace_od, prace_do FROM Doktori_Ordinacni_Cas
                      WHERE doktor_id = %s AND datum = %s AND ordinace_id = %s
                  ''', (doktor_id, datum_str, ordinace_id))
                  zaznamy = cur.fetchall()

                  # print(f"Záznamy ordinačních časů: {zaznamy}")

                  for zaznam_id, exist_od, exist_do in zaznamy:
                      exist_od_dt = datetime.strptime(exist_od, "%H:%M")
                      exist_do_dt = datetime.strptime(exist_do, "%H:%M")

                      # Nový úsek zcela překrývá starý
                      if prace_od_dt <= exist_od_dt and prace_do_dt >= exist_do_dt:
                          # print("Nový úsek zcela překrývá starý")
                          cur.execute('DELETE FROM Doktori_Ordinacni_Cas WHERE work_id = %s', (zaznam_id,))
                          conn.commit()
                      # Nový úsek překrývá začátek starého
                      elif prace_od_dt <= exist_od_dt <= prace_do_dt <= exist_do_dt:
                          # print("Nový úsek překrývá začátek starého")
                          exist_do_dt = time_anchores[time_anchores.index(prace_do)+1]
                          cur.execute('UPDATE Doktori_Ordinacni_Cas SET prace_od = %s WHERE work_id = %s', (exist_do_dt, zaznam_id))
                          conn.commit()
                      # Nový úsek překrývá konec starého
                      elif exist_od_dt < prace_od_dt <= exist_do_dt <= prace_do_dt:
                          # print("Nový úsek překrývá konec starého")
                          exist_do_dt = time_anchores[time_anchores.index(prace_od)-1]
                          cur.execute('UPDATE Doktori_Ordinacni_Cas SET prace_do = %s WHERE work_id = %s', (exist_do_dt, zaznam_id))
                          conn.commit()
                          
                      # Nový úsek je uvnitř starého (rozdělení na dva)
                      elif exist_od_dt < prace_od_dt and prace_do_dt < exist_do_dt:
                          # print("Nový úsek je uvnitř starého a rozdělí ho na dva")
                          exist_do_dt = time_anchores[time_anchores.index(prace_od)-1]
                          exist_new_od_dt = time_anchores[time_anchores.index(prace_od)+1]
                          cur.execute('UPDATE Doktori_Ordinacni_Cas SET prace_do = %s WHERE work_id = %s', (exist_do_dt, zaznam_id))
                          cur.execute('''
                              INSERT INTO Doktori_Ordinacni_Cas (doktor_id, datum, prace_od, prace_do, ordinace_id)
                              VALUES (%s, %s, %s, %s, %s)
                          ''', (doktor_id, datum_str, exist_new_od_dt, exist_do, ordinace_id))
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
        WHERE Doktori_Ordinacni_Cas.datum = %s
        ORDER BY Doktori_Ordinacni_Cas.prace_od
        ''', (den_v_tydnu,))
        return cur.fetchall()
      
def remove_all_ordinacni_cas(ordinace_id):
    """Odstraní všechny ordinační časy pro daného doktora."""
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute('''
            DELETE FROM Doktori_Ordinacni_Cas WHERE ordinace_id = %s
        ''', (ordinace_id,))
        conn.commit()


def check_doctor_reservations(doktor_id):
    """Zkontroluje, zda má doktor nějaké rezervace."""
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute('''
            SELECT COUNT(*) FROM Rezervace WHERE doktor_id = %s
        ''', (doktor_id,))
        count = cur.fetchone()[0]
        return count > 0


def deactivate_doctor(doktor_id):
    """Deaktivuje doktora místo smazání."""
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute('''
            UPDATE Doktori SET isActive = FALSE WHERE doktor_id = %s
        ''', (doktor_id,))
        conn.commit()


def remove_doctor(doktor_id):
    """Odstraní doktora z databáze - pouze pokud nemá rezervace."""
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute('''
            DELETE FROM Doktori WHERE doktor_id = %s
        ''', (doktor_id,))
        conn.commit()
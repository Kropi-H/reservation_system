from models.databaze import get_connection

def pridej_rezervaci(pacient, doktor, cas, mistnost):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO rezervace (pacient, doktor, cas, mistnost) VALUES (?, ?, ?, ?)",
                  (pacient, doktor, cas, mistnost))
    conn.commit()
    conn.close()

def ziskej_rezervace_dne(datum_str):
    """
    Vrátí seznam rezervací pro daný den (datum ve formátu 'YYYY-MM-DD').
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM rezervace WHERE DATE(cas) = ?", (datum_str,))
    data = cursor.fetchall()
    conn.close()
    return data

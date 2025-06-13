from models.databaze import get_connection

def get_all_ordinace():
    """Získá všechny ordinace z databáze."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM ordinace")
    ordinace = cursor.fetchall()
    cursor.close()
    return ordinace
  
def get_ordinace_by_id(ordinace_id):
    """Získá ordinaci podle ID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Ordinace WHERE ordinace_id = ?", (ordinace_id,))
    ordinace = cursor.fetchone()
    cursor.close()
    return ordinace 
  
def add_ordinace(nazev, patro, popis):
    """Přidá novou ordinaci do databáze."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO ordinace (nazev, patro, popis) VALUES (?, ?, ?)", (nazev, patro, popis))
    conn.commit()
    cursor.close()
    
def remove_ordinace(ordinace_id):
    """Odstraní ordinaci z databáze podle ID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM ordinace WHERE id = ?", (ordinace_id,))
    conn.commit()
    cursor.close()
    
def update_ordinace_db(ordinace_id, data):
    """Aktualizuje údaje ordinace v databázi."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE Ordinace SET nazev = ?, patro = ?, popis = ? WHERE ordinace_id = ?", (data['nazev'], data['patro'], data['popis'], ordinace_id))
    conn.commit()
    cursor.close()
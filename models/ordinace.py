from models.databaze import get_connection
from psycopg2.extras import RealDictCursor

def get_all_ordinace():
    """Získá všechny ordinace z databáze."""
    with get_connection() as conn:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("SELECT * FROM Ordinace ORDER BY nazev")
        ordinace = cursor.fetchall()
        cursor.close()
        return ordinace
  
def get_ordinace_by_id(ordinace_id):
    """Získá ordinaci podle ID."""
    with get_connection() as conn:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("SELECT * FROM Ordinace WHERE ordinace_id = %s", (ordinace_id,))
        ordinace = cursor.fetchone()
        cursor.close()
        return ordinace 
  
def add_ordinace(data):
    """Přidá novou ordinaci do databáze."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO Ordinace (nazev, patro, popis) VALUES (%s, %s, %s)", (data['nazev'], data['patro'], data['popis']))
        conn.commit()
        cursor.close()
    
def remove_ordinace(ordinace_id, nazev):
    """Odstraní ordinaci z databáze podle ID."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM Ordinace WHERE ordinace_id = %s AND nazev = %s", (ordinace_id, nazev))
        conn.commit()
        cursor.close()
    
def update_ordinace_db(ordinace_id, data):
    """Aktualizuje údaje ordinace v databázi."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE Ordinace SET nazev = %s, patro = %s, popis = %s WHERE ordinace_id = %s", (data['nazev'], data['patro'], data['popis'], ordinace_id))
        conn.commit()
        cursor.close()
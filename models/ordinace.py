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
    cursor.execute("SELECT * FROM ordinace WHERE id = ?", (ordinace_id,))
    ordinace = cursor.fetchone()
    cursor.close()
    return ordinace
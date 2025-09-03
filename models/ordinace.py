from models.databaze import get_connection
from psycopg2.extras import RealDictCursor

# Import pro database notifikace (pouze pokud je dostupný)
try:
    from models.database_listener import notify_database_change
    NOTIFICATIONS_ENABLED = True
except ImportError:
    NOTIFICATIONS_ENABLED = False
    def notify_database_change(*args, **kwargs):
        pass

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
        cursor.execute("INSERT INTO Ordinace (nazev, patro, popis) VALUES (%s, %s, %s) RETURNING ordinace_id", 
                      (data['nazev'], data['patro'], data['popis']))
        ordinace_id = cursor.fetchone()[0]
        conn.commit()
        cursor.close()
        
        # Pošli notifikaci o nové ordinaci
        if NOTIFICATIONS_ENABLED:
            notify_database_change('ordinace', 'INSERT', {
                'id': ordinace_id,
                'nazev': data['nazev'],
                'patro': data['patro'],
                'popis': data['popis']
            })
    
def remove_ordinace(ordinace_id, nazev):
    """Odstraní ordinaci z databáze podle ID."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM Ordinace WHERE ordinace_id = %s AND nazev = %s", (ordinace_id, nazev))
        removed = cursor.rowcount > 0
        conn.commit()
        cursor.close()
        
        # Pošli notifikaci o odstranění ordinace
        if removed and NOTIFICATIONS_ENABLED:
            notify_database_change('ordinace', 'DELETE', {
                'id': ordinace_id,
                'nazev': nazev
            })
    
def update_ordinace_db(ordinace_id, data):
    """Aktualizuje údaje ordinace v databázi."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE Ordinace SET nazev = %s, patro = %s, popis = %s WHERE ordinace_id = %s", 
                      (data['nazev'], data['patro'], data['popis'], ordinace_id))
        updated = cursor.rowcount > 0
        conn.commit()
        cursor.close()
        
        # Pošli notifikaci o úpravě ordinace
        if updated and NOTIFICATIONS_ENABLED:
            notify_database_change('ordinace', 'UPDATE', {
                'id': ordinace_id,
                'nazev': data['nazev'],
                'patro': data['patro'],
                'popis': data['popis']
            })
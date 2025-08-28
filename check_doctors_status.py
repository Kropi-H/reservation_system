from models.databaze import get_connection
from psycopg2.extras import RealDictCursor

with get_connection() as conn:
    cur = conn.cursor(cursor_factory=RealDictCursor)
    print('=== VŠICHNI DOKTOŘI ===')
    cur.execute('SELECT doktor_id, jmeno, prijmeni, isactive FROM Doktori ORDER BY jmeno, prijmeni')
    all_docs = cur.fetchall()
    for doc in all_docs:
        name = f"{doc['jmeno'].strip()} {doc['prijmeni'].strip()}"
        status = 'AKTIVNÍ' if doc['isactive'] == 1 else 'NEAKTIVNÍ'
        print(f'ID {doc["doktor_id"]}: {name} - {status}')
    
    print()
    print('=== POUZE AKTIVNÍ ===')
    cur.execute('SELECT doktor_id, jmeno, prijmeni FROM Doktori WHERE isactive = 1 ORDER BY jmeno, prijmeni')
    active_docs = cur.fetchall()
    for doc in active_docs:
        name = f"{doc['jmeno'].strip()} {doc['prijmeni'].strip()}"
        print(f'ID {doc["doktor_id"]}: {name}')
    
    print(f'\nCelkem doktorů: {len(all_docs)}, Aktivních: {len(active_docs)}')

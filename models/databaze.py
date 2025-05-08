import sqlite3

def get_connection():
    return sqlite3.connect("veterina.db")

def inicializuj_databazi():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS rezervace (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        pacient TEXT NOT NULL,
        doktor TEXT NOT NULL,
        cas TEXT NOT NULL,
        mistnost TEXT NOT NULL
    )''')
    conn.commit()
    conn.close()
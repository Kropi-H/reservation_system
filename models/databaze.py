import sqlite3

DB = "veterina.db"

def inicializuj_databazi():
    """Vytvoří tabulky Doktori, Ordinace, Pacienti a Rezervace, pokud neexistují."""
    with get_connection() as conn:
        cur = conn.cursor()
        # 1) Doktoři
        cur.execute('''
        CREATE TABLE IF NOT EXISTS Doktori (
            doktor_id     INTEGER PRIMARY KEY AUTOINCREMENT,
            jmeno         TEXT    NOT NULL,
            prijmeni      TEXT    NOT NULL,
            specializace  TEXT,
            isActive      INTEGER,
            color         TEXT
        );
        ''')

        # 2) Ordinace
        cur.execute('''
        CREATE TABLE IF NOT EXISTS Ordinace (
            ordinace_id   INTEGER PRIMARY KEY AUTOINCREMENT,
            nazev         TEXT    NOT NULL,
            patro         INTEGER,
            popis         TEXT
        );
        ''')

        # 3) Pacienti
        cur.execute('''
        CREATE TABLE IF NOT EXISTS Pacienti (
            pacient_id      INTEGER PRIMARY KEY AUTOINCREMENT,
            jmeno_zvirete   TEXT    NOT NULL,
            druh            TEXT    NOT NULL,
            majitel_jmeno   TEXT,
            majitel_telefon TEXT,
            poznamka       TEXT
        );
        ''')

        # 4) Rezervace
        cur.execute('''
        CREATE TABLE IF NOT EXISTS Rezervace (
            rezervace_id   INTEGER PRIMARY KEY AUTOINCREMENT,
            pacient_id     INTEGER    NOT NULL,
            doktor_id      INTEGER    NOT NULL,
            ordinace_id    INTEGER    NOT NULL,
            termin         DATETIME   NOT NULL,
            FOREIGN KEY(pacient_id) REFERENCES Pacienti(pacient_id)
                ON DELETE CASCADE,
            FOREIGN KEY(doktor_id)  REFERENCES Doktori(doktor_id)
                ON DELETE RESTRICT,
            FOREIGN KEY(ordinace_id)REFERENCES Ordinace(ordinace_id)
                ON DELETE RESTRICT
        );
        ''')
        conn.commit()

def get_connection():
    conn = sqlite3.connect(DB)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def get_or_create(cur, table, unique_cols, data_cols):
    """
    Zkusí najít záznam podle unique_cols (tuple sloupců).
    Pokud neexistuje, vloží nový.
    Vrátí id (lastrowid nebo existující id).
    """
    # WHERE jmeno=? AND prijmeni=? …
    where_clause = " AND ".join(f"{col}=?" for col in unique_cols)
    params_where  = tuple(data_cols[col] for col in unique_cols)
    cur.execute(
        f"SELECT rowid FROM {table} WHERE {where_clause}",
        params_where
    )
    row = cur.fetchone()
    if row:
        return row[0]

    # Vloží nový záznam
    cols  = ", ".join(data_cols.keys())
    vals  = ", ".join("?" for _ in data_cols)
    params = tuple(data_cols.values())
    cur.execute(
        f"INSERT INTO {table} ({cols}) VALUES ({vals})",
        params
    )
    return cur.lastrowid

def get_doktori():
    """Vrátí seznam všech doktorů."""
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute('''
        SELECT doktor_id, jmeno, prijmeni 
        FROM Doktori
        WHERE isActive = 1
        ''')
        return cur.fetchall()
    
def get_ordinace():
    """Vrátí seznam všech ordinací."""
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute('''
        SELECT ordinace_id, nazev 
        FROM Ordinace
        ''')
        return cur.fetchall()


"""
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
    """
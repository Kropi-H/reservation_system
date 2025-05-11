import sqlite3

DB_NAME = "veterina.db"

def get_connection():
    """Otevře připojení a zapne podporu cizích klíčů."""
    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

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
            isActive      INTEGER,
            specializace  TEXT
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
            majitel_telefon TEXT
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
            poznamka       TEXT,
            FOREIGN KEY(pacient_id) REFERENCES Pacienti(pacient_id)
                ON DELETE CASCADE,
            FOREIGN KEY(doktor_id)  REFERENCES Doktori(doktor_id)
                ON DELETE RESTRICT,
            FOREIGN KEY(ordinace_id)REFERENCES Ordinace(ordinace_id)
                ON DELETE RESTRICT
        );
        ''')
        conn.commit()

# --- Pomocné CRUD funkce ---

def pridej_doktora(jmeno: str, prijmeni: str, specializace: str = None, isActive: int = 1):
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO Doktori (jmeno, prijmeni, specializace, isActive) VALUES (?, ?, ?, ?)",
            (jmeno, prijmeni, specializace, isActive)
        )
        conn.commit()

def pridej_ordinaci(nazev: str, patro: int = None, popis: str = None):
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO Ordinace (nazev, patro, popis) VALUES (?, ?, ?)",
            (nazev, patro, popis)
        )
        conn.commit()

def pridej_pacienta(jmeno_zvirete: str, druh: str,
                    majitel_jmeno: str = None, majitel_telefon: str = None):
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO Pacienti (jmeno_zvirete, druh, majitel_jmeno, majitel_telefon) "
            "VALUES (?, ?, ?, ?)",
            (jmeno_zvirete, druh, majitel_jmeno, majitel_telefon)
        )
        conn.commit()

def pridej_rezervaci(pacient_id: int, doktor_id: int, ordinace_id: int,
  termin: str, poznamka: str = None):
    """
    termin: řetězec ve formátu 'YYYY-MM-DD HH:MM:SS'
    """
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO Rezervace (pacient_id, doktor_id, ordinace_id, termin, poznamka) "
            "VALUES (?, ?, ?, ?, ?)",
            (pacient_id, doktor_id, ordinace_id, termin, poznamka)
        )
        conn.commit()

def seznam_rezervaci():
    """Vrátí všechny rezervace s jejich doktorem, pacientem a ordinací."""
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute('''
        SELECT
            r.rezervace_id,
            p.jmeno_zvirete || ' (' || p.druh || ')' AS pacient,
            d.jmeno || ' ' || d.prijmeni         AS doktor,
            o.nazev                              AS ordinace,
            r.termin,
            r.poznamka
        FROM Rezervace r
        JOIN Pacienti p ON r.pacient_id   = p.pacient_id
        JOIN Doktori d   ON r.doktor_id    = d.doktor_id
        JOIN Ordinace o  ON r.ordinace_id  = o.ordinace_id
        ORDER BY r.termin;
        ''')
        return cur.fetchall()
  

# --- Příklad použití ---
"""
if __name__ == "__main__":
    inicializuj_databazi()

    # Naplnění ukázkovými daty
    pridej_doktora("Jan", "Novák", "Chirurgie")
    pridej_ordinaci("Ordinace A", patro=1)
    pridej_pacienta("Rex", "Pes", "Petr Dvořák", "+420123456789")
    pridej_rezervaci(
        pacient_id=1,
        doktor_id=1,
        ordinace_id=1,
        termin="2025-05-10 14:30:00",
        poznamka="Pravidelná kontrola"
    )

    # Vypsání všech rezervací
    for rez in seznam_rezervaci():
        print(rez)
"""
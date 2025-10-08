import psycopg2
from psycopg2.extras import RealDictCursor
import os
from config import get_database_config, get_database_type, test_database_connection

# Přidání connection pooling
try:
    from models.connection_pool import PooledConnection, _connection_pool
    USE_POOL = True
except ImportError:
    USE_POOL = False
    print("Connection pool není dostupný, používá se standardní připojení")

# Určení kořenového adresáře projektu
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def get_connection():
    """Získá připojení k PostgreSQL databázi."""
    if USE_POOL:
        try:
            return PooledConnection()
        except Exception as e:
            print(f"Chyba při použití connection pool, fallback na standardní připojení: {e}")
    
    # Fallback na standardní připojení
    config = get_database_config()
    if not config:
        raise Exception("PostgreSQL databáze není nakonfigurována. Spusťte nastavení databáze.")
    
    try:
        conn = psycopg2.connect(**config)
        return conn
    except Exception as e:
        raise Exception(f"Nepodařilo se připojit k PostgreSQL databázi: {e}")

def set_database_path(path):
    """Zachováno pro zpětnou kompatibilitu - pro PostgreSQL se nepoužívá."""
    print("Varování: set_database_path se nepoužívá pro PostgreSQL")

def get_database_path():
    """Zachováno pro zpětnou kompatibilitu - vrací connection string."""
    config = get_database_config()
    if config:
        return f"postgresql://{config['user']}@{config['host']}:{config['port']}/{config['database']}"
    return None

def database_exists():
    """Zkontroluje, zda je PostgreSQL databáze dostupná."""
    return test_database_connection()

def inicializuj_databazi():
    """Vytvoří tabulky v PostgreSQL databázi, pokud neexistují."""
    with get_connection() as conn:
        cur = conn.cursor()
        
        # 1) Doktoři - PostgreSQL syntaxe
        cur.execute('''
        CREATE TABLE IF NOT EXISTS Doktori (
            doktor_id     SERIAL PRIMARY KEY,
            jmeno         VARCHAR(100) NOT NULL,
            prijmeni      VARCHAR(100) NOT NULL,
            specializace  VARCHAR(200),
            isActive      INTEGER DEFAULT 1,
            color         VARCHAR(20)
        );
        ''')

        # 2) Ordinace
        cur.execute('''
        CREATE TABLE IF NOT EXISTS Ordinace (
            ordinace_id   SERIAL PRIMARY KEY,
            nazev         VARCHAR(100) NOT NULL UNIQUE,
            patro         INTEGER,
            popis         TEXT
        );
        ''')
        
        cur.execute('SELECT COUNT(*) FROM Ordinace')
        if cur.fetchone()[0] == 0:
            cur.execute('''
            INSERT INTO Ordinace (nazev, patro, popis)
            VALUES ('Ordinace 1', 1, 'Hlavní ordinace');
            ''')
        
        # 3) Pacienti
        cur.execute('''
        CREATE TABLE IF NOT EXISTS Pacienti (
            pacient_id      SERIAL PRIMARY KEY,
            jmeno_zvirete   VARCHAR(100) NOT NULL,
            druh            VARCHAR(100) NOT NULL,
            majitel_jmeno   VARCHAR(100),
            majitel_telefon VARCHAR(20),
            poznamka        TEXT
        );
        ''')

        # 4) Rezervace
        cur.execute('''
        CREATE TABLE IF NOT EXISTS Rezervace (
            rezervace_id   SERIAL PRIMARY KEY,
            pacient_id     INTEGER NOT NULL,
            doktor_id      INTEGER NOT NULL,
            ordinace_id    INTEGER NOT NULL,
            termin         DATE NOT NULL,
            cas_od         TIME NOT NULL,
            cas_do         TIME NOT NULL,
            created_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(pacient_id) REFERENCES Pacienti(pacient_id)
                ON DELETE CASCADE,
            FOREIGN KEY(doktor_id)  REFERENCES Doktori(doktor_id)
                ON DELETE RESTRICT,
            FOREIGN KEY(ordinace_id) REFERENCES Ordinace(ordinace_id)
                ON DELETE RESTRICT
        );
        ''')
        
        # 5) Ordinační čas doktora
        cur.execute('''
        CREATE TABLE IF NOT EXISTS Doktori_Ordinacni_Cas (
            work_id        SERIAL PRIMARY KEY,
            doktor_id      INTEGER NOT NULL,
            datum          DATE NOT NULL,
            prace_od       TIME NOT NULL,
            prace_do       TIME NOT NULL,
            ordinace_id    INTEGER NOT NULL,
            FOREIGN KEY(doktor_id) REFERENCES Doktori(doktor_id)
                ON DELETE CASCADE,
            FOREIGN KEY(ordinace_id) REFERENCES Ordinace(ordinace_id)
                ON DELETE RESTRICT
        );
        ''')
        
        # 6) Uživatelé
        cur.execute('''
        CREATE TABLE IF NOT EXISTS Users (
            user_id      SERIAL PRIMARY KEY,
            username     VARCHAR(50) NOT NULL UNIQUE,
            password     VARCHAR(255) NOT NULL,
            user_role    VARCHAR(20) NOT NULL
        );
        ''')
                
        # 7) Nastavení
        cur.execute('''
        CREATE TABLE IF NOT EXISTS Settings (
            setting_id    SERIAL PRIMARY KEY,
            setting_name  VARCHAR(50) NOT NULL UNIQUE,
            setting_value TEXT NOT NULL
        );
        ''')
        
        cur.execute('SELECT COUNT(*) FROM Settings')
        if cur.fetchone()[0] == 0:
            cur.execute('''
            INSERT INTO Settings (setting_name, setting_value)
            VALUES ('days_to_keep', '0');
            ''')

        # Upgrade databáze - přidání sloupce stav do tabulky Rezervace
        try:
            cur.execute('''
            ALTER TABLE Rezervace 
            ADD COLUMN IF NOT EXISTS stav VARCHAR(20) DEFAULT NULL;
            ''')
        except Exception as e:
            # Sloupec už možná existuje, pokračujeme
            pass

        # Vytvoření indexů pro výkon
        cur.execute('''
        CREATE INDEX IF NOT EXISTS idx_rezervace_termin_cas 
        ON Rezervace(termin, cas_od);
        ''')
        
        cur.execute('''
        CREATE INDEX IF NOT EXISTS idx_rezervace_doktor 
        ON Rezervace(doktor_id);
        ''')
        
        cur.execute('''
        CREATE INDEX IF NOT EXISTS idx_doktori_ordinacni_cas_datum 
        ON Doktori_Ordinacni_Cas(datum, doktor_id);
        ''')

        conn.commit()
        

def get_or_create(cur, table, unique_cols, data_cols):
    """
    Zkusí najít záznam podle unique_cols (tuple sloupců).
    Pokud neexistuje, vloží nový.
    Vrátí id (SERIAL primary key).
    """
    # PostgreSQL používá %s místo ?
    where_clause = " AND ".join(f"{col}=%s" for col in unique_cols)
    params_where = tuple(data_cols[col] for col in unique_cols)
    
    # Určení primary key názvu podle tabulky
    pk_mapping = {
        "Doktori": "doktor_id",
        "Ordinace": "ordinace_id", 
        "Pacienti": "pacient_id",
        "Rezervace": "rezervace_id",
        "Doktori_Ordinacni_Cas": "work_id",
        "Users": "user_id",
        "Settings": "setting_id"
    }
    primary_key = pk_mapping.get(table, f"{table.lower()}_id")
    
    cur.execute(
        f"SELECT {primary_key} FROM {table} WHERE {where_clause}",
        params_where
    )
    row = cur.fetchone()
    if row:
        return row[0]

    # Vloží nový záznam s RETURNING clause
    cols = ", ".join(data_cols.keys())
    vals = ", ".join("%s" for _ in data_cols)
    params = tuple(data_cols.values())
    
    cur.execute(
        f"INSERT INTO {table} ({cols}) VALUES ({vals}) RETURNING {primary_key}",
        params
    )
    return cur.fetchone()[0]

def get_doktori():
    """Vrátí seznam všech aktivních doktorů."""
    with get_connection() as conn:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute('''
        SELECT doktor_id, jmeno, prijmeni, isActive, specializace, color
        FROM Doktori
        WHERE isActive = 1
        ORDER BY jmeno, prijmeni
        ''')
        return cur.fetchall()
    
def get_ordinace():
    """Vrátí seznam všech ordinací."""
    with get_connection() as conn:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute('''
        SELECT ordinace_id, nazev 
        FROM Ordinace
        ORDER BY nazev
        ''')
        return cur.fetchall()

def get_user_by_username(username):
    """Najde uživatele podle username."""
    with get_connection() as conn:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute(
            "SELECT username, password, user_role FROM Users WHERE username = %s", 
            (username,)
        )
        row = cur.fetchone()
        if row:
            return {
                'username': row['username'], 
                'password_hash': row['password'], 
                'role': row['user_role']
            }
        return None
# Kontrola a inicializace PostgreSQL databáze při importu
config = get_database_config()
if config and test_database_connection():
    try:
        # Zkontroluj, zda má databáze správné tabulky
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute("""
                SELECT table_name FROM information_schema.tables 
                WHERE table_schema = 'public' AND table_name = 'doktori'
            """)
            if not cur.fetchone():
                print("PostgreSQL databáze je připojena, ale chybí tabulky. Inicializuji...")
                inicializuj_databazi()
            else:
                print("PostgreSQL databáze je připravena k použití.")
    except Exception as e:
        print(f"Chyba při kontrole PostgreSQL databáze: {e}")
elif config:
    print("⚠️  Konfigurace PostgreSQL databáze existuje, ale připojení se nezdařilo.")
    print("   Zkontrolujte, zda je PostgreSQL server spuštěn a dostupný.")
    print(f"   Host: {config.get('host', 'N/A')}")
    print(f"   Port: {config.get('port', 'N/A')}")
    print(f"   Database: {config.get('database', 'N/A')}")
else:
    print("⚠️  PostgreSQL databáze není nakonfigurována.")
    print("   Spusťte aplikaci a projděte nastavením databáze.")
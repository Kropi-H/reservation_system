from models.databaze import get_connection
from psycopg2.extras import RealDictCursor

def get_settings(setting_name):
    """Získá nastavení z databáze."""
    with get_connection() as conn:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute('''
                       SELECT setting_value FROM Settings
                       WHERE setting_name = %s
                       ''', (setting_name,))
        settings = cursor.fetchone()
        cursor.close()
        return int(settings['setting_value']) if settings else 0

def save_settings(settings):
    """Uloží nastavení do databáze."""
    with get_connection() as conn:
        cursor = conn.cursor()
        for key, value in settings.items():
            # PostgreSQL UPSERT pomocí ON CONFLICT
            cursor.execute('''
                INSERT INTO Settings (setting_name, setting_value) 
                VALUES (%s, %s) 
                ON CONFLICT (setting_name) 
                DO UPDATE SET setting_value = EXCLUDED.setting_value
            ''', (key, str(value)))
        conn.commit()
        cursor.close()

from models.databaze import get_connection

def get_settings(setting_name):
    """Získá nastavení z databáze."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
                   SELECT * FROM Settings
                   WHERE setting_name = ?
                   ''', (setting_name,))
    settings = cursor.fetchone()
    cursor.close()
    return settings[2] if settings else 0

def save_settings(settings):
    """Uloží nastavení do databáze."""
    conn = get_connection()
    cursor = conn.cursor()
    for key, value in settings.items():
        cursor.execute("INSERT OR REPLACE INTO Settings (setting_name, setting_value) VALUES (?, ?)", (key, value))
    conn.commit()
    cursor.close()

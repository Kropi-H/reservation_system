import sys
from views.database_setup_dialog import DatabaseSetupDialog
from models.databaze import inicializuj_databazi, database_exists
from config import get_database_config, get_database_type, test_database_connection
from PySide6.QtWidgets import QApplication, QMessageBox
import os

def setup_database():
    """Zkontroluje a nastaví připojení k PostgreSQL databázi před spuštěním aplikace."""
    # Zkontroluj typ databáze a konfiguraci
    db_type = get_database_type()
    
    if db_type == 'postgresql':
        return setup_postgresql_database()
    else:
        # Pro SQLite (pro zpětnou kompatibilitu)
        return setup_sqlite_database()

def setup_postgresql_database():
    """Nastaví PostgreSQL databázi."""
    # Zkontroluj, zda je nastavena konfigurace databáze
    db_config = get_database_config()
    
    # Pokud konfigurace neexistuje nebo připojení nefunguje
    if not db_config or not test_database_connection():
        # Zobraz informační zprávu
        temp_app = QApplication.instance()
        if temp_app is None:
            temp_app = QApplication(sys.argv)
        
        QMessageBox.information(
            None,
            "PostgreSQL databáze",
            "PostgreSQL databáze je již nakonfigurována a připravena k použití.\n\n"
            f"Server: {db_config.get('host', 'localhost') if db_config else 'localhost'}\n"
            f"Databáze: {db_config.get('database', 'veterina') if db_config else 'veterina'}\n"
            f"Uživatel: {db_config.get('user', 'postgres') if db_config else 'postgres'}"
        )
        
        # Pokud připojení nefunguje, ukončí aplikaci
        if not test_database_connection():
            QMessageBox.critical(
                None,
                "Chyba připojení",
                "Nepodařilo se připojit k PostgreSQL databázi.\n"
                "Zkontrolujte, zda je PostgreSQL server spuštěn."
            )
            return False
    
    # Zkontroluj a inicializuj databázové schéma
    try:
        inicializuj_databazi()
        print("✅ PostgreSQL databáze je připravena")
        return True
    except Exception as e:
        temp_app = QApplication.instance()
        if temp_app is None:
            temp_app = QApplication(sys.argv)
            
        QMessageBox.critical(
            None,
            "Chyba",
            f"Nepodařilo se inicializovat PostgreSQL databázi:\n{str(e)}"
        )
        return False

def setup_sqlite_database():
    """Starý způsob pro SQLite (zachováno pro kompatibilitu)."""
    from models.databaze import set_database_path, get_database_path
    
    # Zkontroluj, zda je nastavena cesta k databázi a zda databáze existuje
    database_path = get_database_path()
    
    # Pokud je cesta prázdná nebo databáze neexistuje, zobraz dialog
    if not database_path or database_path == "" or not os.path.exists(database_path):
        # Vytvoř aplikaci pro zobrazení dialogu
        temp_app = QApplication.instance()
        if temp_app is None:
            temp_app = QApplication(sys.argv)
        
        # Zobraz dialog pro nastavení databáze
        dialog = DatabaseSetupDialog()
        result = dialog.exec()
        
        if result == DatabaseSetupDialog.Accepted:
            selected_path = dialog.get_database_path()
            set_database_path(selected_path)
            
            # Pokud byla vybrána nová databáze, inicializuj ji
            if not os.path.exists(selected_path):
                try:
                    inicializuj_databazi()
                    QMessageBox.information(
                        None,
                        "Úspěch", 
                        f"Nová SQLite databáze byla úspěšně vytvořena: {selected_path}"
                    )
                except Exception as e:
                    QMessageBox.critical(
                        None,
                        "Chyba",
                        f"Nepodařilo se vytvořit SQLite databázi: {str(e)}"
                    )
                    return False
            else:
                # Existující databáze - zkontroluj a případně aktualizuj strukturu
                try:
                    inicializuj_databazi()
                    QMessageBox.information(
                        None,
                        "Úspěch", 
                        f"SQLite databáze byla úspěšně připojena: {selected_path}"
                    )
                except Exception as e:
                    QMessageBox.critical(
                        None,
                        "Chyba",
                        f"Nepodařilo se připojit k SQLite databázi: {str(e)}"
                    )
                    return False
        else:
            # Uživatel zrušil dialog nebo zvolil ukončení
            return False
    else:
        # Databáze existuje, pouze ji inicializuj
        try:
            inicializuj_databazi()
        except Exception as e:
            QMessageBox.critical(
                None,
                "Chyba",
                f"Nepodařilo se připojit k SQLite databázi: {str(e)}"
            )
            return False
    
    return True
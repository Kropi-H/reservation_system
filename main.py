from models.databaze import inicializuj_databazi, set_database_path, database_exists, get_database_path
from PySide6.QtWidgets import QApplication, QMessageBox
from views.hlavni_okno import HlavniOkno
from views.database_setup_dialog import DatabaseSetupDialog
import sys
import os

def setup_database():
    """Zkontroluje a nastaví databázi před spuštěním aplikace."""
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
                        f"Nová databáze byla úspěšně vytvořena: {selected_path}"
                    )
                except Exception as e:
                    QMessageBox.critical(
                        None,
                        "Chyba",
                        f"Nepodařilo se vytvořit databázi: {str(e)}"
                    )
                    return False
            else:
                # Existující databáze - zkontroluj a případně aktualizuj strukturu
                try:
                    inicializuj_databazi()
                    QMessageBox.information(
                        None,
                        "Úspěch", 
                        f"Databáze byla úspěšně připojena: {selected_path}"
                    )
                except Exception as e:
                    QMessageBox.critical(
                        None,
                        "Chyba",
                        f"Nepodařilo se připojit k databázi: {str(e)}"
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
                f"Nepodařilo se připojit k databázi: {str(e)}"
            )
            return False
    
    return True

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Nastavení databáze
    if not setup_database():
        sys.exit(1)
    
    # Spuštění hlavního okna
    okno = HlavniOkno()
    okno.showMaximized()  # Maximalizace okna při startu
    okno.show()
    sys.exit(app.exec())
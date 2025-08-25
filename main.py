from PySide6.QtWidgets import QApplication, QMessageBox
from views.postgresql_setup_dialog import PostgreSQLSetupDialog
from config import test_database_connection, get_database_config

import sys

def check_database_connection():
    """Zkontroluje připojení k databázi a zobrazí konfigurační dialog pokud je potřeba."""
    
    # Zkusí se připojit k databázi
    if test_database_connection():
        return True
    
    # Pokud připojení selhalo, zobraz konfigurační dialog
    print("⚠️ Databáze není dostupná. Zobrazuji konfigurační dialog...")
    
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    
    # Zobrazit PostgreSQL konfigurační dialog
    dialog = PostgreSQLSetupDialog()
    result = dialog.exec()
    
    if result == PostgreSQLSetupDialog.Accepted:
        if dialog.is_connection_successful():
            print("✅ Databáze byla úspěšně nakonfigurována")
            return True
        else:
            print("❌ Konfigurace databáze selhala")
            return False
    else:
        print("❌ Uživatel zrušil konfiguraci databáze")
        return False

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Kontrola a konfigurace databáze
    if not check_database_connection():
        QMessageBox.critical(
            None,
            "Chyba databáze",
            "Aplikace nemůže být spuštěna bez připojení k databázi.\n"
            "Zkontrolujte konfiguraci PostgreSQL serveru a zkuste to znovu."
        )
        sys.exit(1)
    
    # Teprve nyní můžeme importovat a spustit hlavní části aplikace
    from views.hlavni_okno import HlavniOkno
    from setup_databaze import setup_database
    from setup_admin import setup_admin
    
    # Nastavení databáze
    if not setup_database() or not setup_admin():
        sys.exit(1)

    # Spuštění hlavního okna
    okno = HlavniOkno()
    okno.showMaximized()  # Maximalizace okna při startu
    okno.show()
    sys.exit(app.exec())
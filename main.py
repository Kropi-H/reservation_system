from PySide6.QtWidgets import QApplication
from views.hlavni_okno import HlavniOkno
from setup_databaze import setup_database
from setup_admin import setup_admin

import sys

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Nastavení databáze
    if not setup_database() or not setup_admin():
        sys.exit(1)

    # Spuštění hlavního okna
    okno = HlavniOkno()
    okno.showMaximized()  # Maximalizace okna při startu
    okno.show()
    sys.exit(app.exec())
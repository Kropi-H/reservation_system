from models.databaze import inicializuj_databazi
from PySide6.QtWidgets import QApplication
from views.hlavni_okno import HlavniOkno
import sys

if __name__ == "__main__":
    inicializuj_databazi()  # << přidáno
    app = QApplication(sys.argv)
    okno = HlavniOkno()
    okno.showMaximized()  # Maximalizace okna při startu
    okno.show()
    sys.exit(app.exec())
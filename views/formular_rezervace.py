# views/formular_rezervace.py
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLineEdit, QPushButton, QLabel, QFormLayout
from controllers.rezervace_controller import uloz_rezervaci

class FormularRezervace(QWidget):
    def __init__(self, hlavni_okno=None):
        super().__init__()
        self.setWindowTitle("Nová rezervace")
        self.hlavni_okno = hlavni_okno  # <- uložíme odkaz

        self.layout = QFormLayout()

        self.pacient_input = QLineEdit()
        self.doktor_input = QLineEdit()
        self.cas_input = QLineEdit()
        self.mistnost_input = QLineEdit()

        self.layout.addRow("Pacient:", self.pacient_input)
        self.layout.addRow("Doktor:", self.doktor_input)
        self.layout.addRow("Čas (např. 2025-05-06 13:30):", self.cas_input)
        self.layout.addRow("Místnost:", self.mistnost_input)

        self.btn_uloz = QPushButton("Uložit rezervaci")
        self.btn_uloz.clicked.connect(self.uloz)
        self.layout.addRow(self.btn_uloz)

        self.status = QLabel()
        self.layout.addRow(self.status)

        self.setLayout(self.layout)

    def uloz(self):
        pacient = self.pacient_input.text()
        doktor = self.doktor_input.text()
        cas = self.cas_input.text()
        mistnost = self.mistnost_input.text()

        if uloz_rezervaci(pacient, doktor, cas, mistnost):
            self.status.setText("Rezervace byla uložena.")
            if self.hlavni_okno:
                self.hlavni_okno.nacti_rezervace()  # <- aktualizujeme hlavní okno
        else:
            self.status.setText("Chyba při ukládání.")

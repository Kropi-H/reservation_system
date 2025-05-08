# views/formular_rezervace.py
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLineEdit, QPushButton, QLabel, QFormLayout, QComboBox
from controllers.rezervace_controller import uloz_rezervaci
from controllers.data import doktori, ordinace



class FormularRezervace(QWidget):
    def __init__(self, hlavni_okno=None):
        super().__init__()
        self.setWindowTitle("Nová rezervace")
        self.hlavni_okno = hlavni_okno  # <- uložíme odkaz
        
        self.layout = QFormLayout()

        self.pacient_jmeno_input = QLineEdit()
        self.pacient_druh_input = QLineEdit()
        self.majitel_input = QLineEdit()
        self.kontakt_majitel_input = QLineEdit()
        self.doktor_input = QComboBox()
        self.doktor_input.addItems(self.get_doctors())  
        self.cas_input = QLineEdit()
        self.mistnost_input = QComboBox()
        self.mistnost_input.addItems(self.get_ordinace())

        self.layout.addRow("Jméno pacienta:", self.pacient_jmeno_input)
        self.layout.addRow("Druh:", self.pacient_druh_input)
        self.layout.addRow("Příjmení majitele:", self.majitel_input)
        self.layout.addRow("Kontakt na majitele:", self.kontakt_majitel_input)
        self.layout.addRow("Doktor:", self.doktor_input)
        self.layout.addRow("Čas (např. 2025-05-06 13:30):", self.cas_input)
        self.layout.addRow("Místnost:", self.mistnost_input)

        self.btn_uloz = QPushButton("Uložit rezervaci")
        #self.btn_uloz.clicked.connect(self.uloz)
        self.btn_uloz.clicked.connect(self.print_data)
        self.layout.addRow(self.btn_uloz)

        self.status = QLabel()
        self.layout.addRow(self.status)

        self.setLayout(self.layout)

    # Test for recieving data
    def print_data(self):
        pacient_jmeno = self.pacient_jmeno_input.text()
        pacient_druh = self.pacient_druh_input.text()
        majitel_pacienta = self.majitel_input.text()
        majitel_kontakt = self.kontakt_majitel_input.text()
        doktor = self.doktor_input.currentText()
        cas = self.cas_input.text()
        mistnost = self.mistnost_input.currentText()
        print(f"Pacient:{pacient_jmeno}, Druh:{pacient_druh}, Majitel:{majitel_pacienta}, Kontakt:{majitel_kontakt}, Doktor:{doktor}, Čas:{cas}, Místnost:{mistnost}")

    def get_doctors(self):
        return [ f"{i['jmeno']} {i['prijmeni']}" for i in doktori]
    
    def get_ordinace(self):
        return [ f"{i['nazev']}" for i in ordinace]

    def uloz(self):
        pacient = self.pacient_input.text()
        doktor = self.doktor_input.currentText()
        cas = self.cas_input.text()
        mistnost = self.mistnost_input.text()

        if uloz_rezervaci(pacient, doktor, cas, mistnost):
            self.status.setText("Rezervace byla uložena.")
            if self.hlavni_okno:
                self.hlavni_okno.nacti_rezervace()  # <- aktualizujeme hlavní okno
        else:
            self.status.setText("Chyba při ukládání.")

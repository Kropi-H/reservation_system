# views/formular_rezervace.py
from PySide6.QtWidgets import QWidget, QHBoxLayout, QLineEdit, QPushButton, QLabel, QFormLayout, QComboBox, QTextEdit
from PySide6.QtCore import QSize
from controllers.rezervace_controller import uloz_rezervaci
from models.databaze import get_doktori, get_ordinace

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
        self.doktor_input.addItem("!---Vyberte doktora---!")
        self.doktor_input.addItems(self.get_doctors())  
        self.cas_input = QLineEdit()
        self.note_input = QTextEdit()
        self.note_input.setTextColor("red")
        self.mistnost_input = QComboBox()
        self.mistnost_input.addItem("!---Vyberte ordinaci---!")
        self.mistnost_input.addItems(self.get_ordinace_list())

        self.layout.addRow("Jméno pacienta:", self.pacient_jmeno_input)
        self.layout.addRow("Druh:", self.pacient_druh_input)
        self.layout.addRow("Příjmení majitele:", self.majitel_input)
        self.layout.addRow("Kontakt na majitele:", self.kontakt_majitel_input)
        self.layout.addRow("Doktor:", self.doktor_input)
        self.layout.addRow("Poznámka:", self.note_input)
        self.layout.addRow("Čas (např. 2025-05-06 13:30):", self.cas_input)
        self.layout.addRow("Místnost:", self.mistnost_input)



        self.btn_uloz = QPushButton("Uložit rezervaci")
        self.btn_uloz.setMaximumSize(200, 100)
        self.btn_uloz.setStyleSheet("background-color: lightblue; font-weight: bold;")
        self.btn_uloz.clicked.connect(self.uloz)
        #self.btn_uloz.clicked.connect(self.print_data)

        v_box = QHBoxLayout()
        v_box.addStretch()
        v_box.addWidget(self.btn_uloz)
        v_box.addStretch()
        self.layout.addRow(v_box)

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
        note = self.note_input.toPlainText()
        cas = self.cas_input.text()
        mistnost = self.mistnost_input.currentText()
        print(f"Pacient:{pacient_jmeno}, Druh:{pacient_druh}, Majitel:{majitel_pacienta}, Kontakt:{majitel_kontakt}, Doktor:{doktor}, Čas:{cas}, Místnost:{mistnost}, Poznámka:{note}")
        self.close() # close the form after printing data

    def get_doctors(self):
        doktori = get_doktori()
        return [ f"{i[1]} {i[2]}" for i in doktori]

    def get_ordinace_list(self):
        ordinace = get_ordinace()
        return [ f"{i[1]}" for i in ordinace]

    def uloz(self):
        pacient_jmeno = self.pacient_jmeno_input.text()
        pacient_druh = self.pacient_druh_input.text()
        majitel_pacienta = self.majitel_input.text()
        majitel_kontakt = self.kontakt_majitel_input.text()
        doktor = self.doktor_input.currentText()
        note = self.note_input.toPlainText()
        cas = self.cas_input.text()
        mistnost = self.mistnost_input.currentText()

        if not pacient_jmeno or not pacient_druh or not majitel_pacienta or not majitel_kontakt or not note or not cas:
          self.status.setText("Vyplňte všechna pole.")
        elif doktor == "!---Vyberte doktora---!":
          self.status.setText("Vybrat doktora.")
        elif mistnost == "!---Vyberte ordinaci---!":
          self.status.setText("Vybrat ordinaci.")
        else:
          # Uložení rezervace
          if uloz_rezervaci(pacient_jmeno, pacient_druh, majitel_pacienta, majitel_kontakt, doktor, note, cas, mistnost):
            self.status.setText("Rezervace byla uložena.")
            if self.hlavni_okno:
                self.hlavni_okno.nacti_rezervace()  # <- aktualizujeme hlavní okno
            self.close()
          else:
            self.status.setText("Chyba při ukládání.")

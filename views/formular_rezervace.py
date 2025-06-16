# views/formular_rezervace.py
from PySide6.QtWidgets import QWidget, QHBoxLayout, QLineEdit, QPushButton, QLabel, QFormLayout, QComboBox, QTextEdit, QDateTimeEdit, QMessageBox
from PySide6.QtCore import QDateTime, QTime
from controllers.rezervace_controller import uloz_rezervaci, odstran_rezervaci_z_db
from models.databaze import get_doktori, get_ordinace


class FormularRezervace(QWidget):
    def __init__(self, hlavni_okno=None, rezervace_data=None, predvyplneny_cas=None, predvyplnena_ordinace=None, predvyplneny_doktor=None):
        super().__init__()
        self.setWindowTitle("Nová rezervace" if rezervace_data is None else "Úprava rezervace")
        self.rezervace_id = rezervace_data[1] if rezervace_data else None
        self.hlavni_okno = hlavni_okno
        self.predvyplneny_doktor = predvyplneny_doktor
        self.rezervace_data = rezervace_data

        self.layout = QFormLayout()

        self.pacient_jmeno_input = QLineEdit()
        self.pacient_druh_input = QLineEdit()
        self.majitel_input = QLineEdit()
        self.kontakt_majitel_input = QLineEdit()
        self.doktor_input = QComboBox()
        self.doktor_input.addItem("!---Vyberte doktora---!")
        self.doktor_input.addItems(self.get_doctors())

        self.cas_input = QDateTimeEdit()
        self.cas_input.setCalendarPopup(True)
        self.cas_input.setDisplayFormat("dd-MM-yyyy HH:mm")
        self.cas_input.setDateTime(QDateTime.currentDateTime())

        self.note_input = QTextEdit()
        self.mistnost_input = QComboBox()
        self.mistnost_input.addItem("!---Vyberte ordinaci---!")
        self.mistnost_input.addItems(self.get_ordinace_list())

        # Předvyplnění dat pokud jsou k dispozici
        if rezervace_data:
          # Předpoklad: rezervace_data = (cas, id, doktor, doktor_color, pacient, majitel, kontakt, druh, mistnost, poznamka)
          self.pacient_jmeno_input.setText(rezervace_data[4])
          self.pacient_druh_input.setText(rezervace_data[7])
          self.majitel_input.setText(rezervace_data[5])
          self.kontakt_majitel_input.setText(rezervace_data[6])
          idx = self.doktor_input.findText(rezervace_data[2]) # index 2 je doktor (jméno)
          if idx != -1:
              self.doktor_input.setCurrentIndex(idx)
          self.note_input.setPlainText(rezervace_data[9])
          dt = QDateTime.fromString(rezervace_data[0], "yyyy-MM-dd HH:mm")
          if dt.isValid():
              self.cas_input.setDateTime(dt)
          idx2 = self.mistnost_input.findText(rezervace_data[8])
          if idx2 != -1:
              self.mistnost_input.setCurrentIndex(idx2)
                
                
        else:
            # Předvyplnění z dvojkliku na prázdný řádek
            if predvyplneny_cas:
                dt = QDateTime.fromString(predvyplneny_cas, "yyyy-MM-dd HH:mm")
                if dt.isValid():
                    self.cas_input.setDateTime(dt)
            if predvyplnena_ordinace:
                idx = self.mistnost_input.findText(predvyplnena_ordinace)
                if idx != -1:
                    self.mistnost_input.setCurrentIndex(idx)
            if predvyplneny_doktor:
                idx = self.doktor_input.findText(predvyplneny_doktor)
                if idx != -1:
                    self.doktor_input.setCurrentIndex(idx)
        '''
        # Použití QDateTimeEdit místo QLineEdit
        self.cas_input = QDateTimeEdit()
        self.cas_input.setCalendarPopup(True)  # Zobrazí kalendář při kliknutí
        self.cas_input.setDisplayFormat("dd-MM-yyyy HH:mm")  # Nastavení formátu data a času
        self.cas_input.setDateTime(QDateTime.currentDateTime())  # Výchozí hodnota je aktuální datum a čas
        
        
        self.note_input = QTextEdit()
        self.mistnost_input = QComboBox()
        self.mistnost_input.addItem("!---Vyberte ordinaci---!")
        self.mistnost_input.addItems(self.get_ordinace_list())
        '''
        # Předvyplnění dat pokud jsou k dispozici
        if rezervace_data:
          # Předpoklad: rezervace_data = (cas, id, doktor, doktor_color, pacient, majitel, kontakt, druh, mistnost, poznamka)
          self.pacient_jmeno_input.setText(rezervace_data[4])
          self.pacient_druh_input.setText(rezervace_data[7])
          self.majitel_input.setText(rezervace_data[5])
          self.kontakt_majitel_input.setText(rezervace_data[6])
          idx = self.doktor_input.findText(rezervace_data[2])  # OPRAVENO: index 2 je doktor
          if idx != -1:
              self.doktor_input.setCurrentIndex(idx)
          self.note_input.setPlainText(rezervace_data[9])
          dt = QDateTime.fromString(rezervace_data[0], "yyyy-MM-dd HH:mm")
          if dt.isValid():
              self.cas_input.setDateTime(dt)
          idx2 = self.mistnost_input.findText(rezervace_data[8])
          if idx2 != -1:
              self.mistnost_input.setCurrentIndex(idx2)

        self.layout.addRow("Jméno pacienta:", self.pacient_jmeno_input)
        self.layout.addRow("Druh:", self.pacient_druh_input)
        self.layout.addRow("Příjmení majitele:", self.majitel_input)
        self.layout.addRow("Kontakt (nemusí být):", self.kontakt_majitel_input)
        self.layout.addRow("Doktor:", self.doktor_input)
        self.layout.addRow("Poznámka (nemusí být):", self.note_input)
        self.layout.addRow("Čas (např. 21-01-2025 09:00):", self.cas_input)
        self.layout.addRow("Ordinace:", self.mistnost_input)



        self.btn_uloz = QPushButton("Uložit rezervaci")
        self.btn_uloz.setMaximumSize(200, 100)
        self.btn_uloz.setStyleSheet("background-color: lightblue; font-weight: bold;color: black;")
        self.btn_uloz.clicked.connect(self.uloz)
        v_box = QHBoxLayout()
        v_box.addStretch()
        v_box.addWidget(self.btn_uloz)
        
        if rezervace_data:
            self.btn_odstran_rezervaci = QPushButton("Odstranit rezervaci")
            self.btn_odstran_rezervaci.setMaximumSize(200, 100)
            self.btn_odstran_rezervaci.setStyleSheet("background-color: #ffcccc; font-weight: bold;color: black;")
            self.btn_odstran_rezervaci.clicked.connect(self.odstran_rezervaci)
            v_box.addWidget(self.btn_odstran_rezervaci)
        #self.btn_uloz.clicked.connect(self.print_data)
        v_box.addStretch()
        self.layout.addRow(v_box)

        self.status = QLabel()
        self.status.setStyleSheet("color: red; font-weight: bold;")
        self.layout.addRow(self.status)

        self.setLayout(self.layout)

    def get_doctors(self):
        doktori = get_doktori()
        return [ f"{i[1]} {i[2]}" for i in doktori]

    def get_ordinace_list(self):
        ordinace = get_ordinace()
        return [ f"{i[1]}" for i in ordinace]
      
    def odstran_rezervaci(self):
        if self.rezervace_id:
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle("Odebrat rezervaci")
            msg_box.setText(f"Odebrat rezervaci pro {self.rezervace_data[4]}, majitel {self.rezervace_data[5]}?")
            ano_button = msg_box.addButton("Ano", QMessageBox.YesRole)
            ne_button = msg_box.addButton("Ne", QMessageBox.NoRole)
            msg_box.exec_()

            if msg_box.clickedButton() == ano_button:
                ok = odstran_rezervaci_z_db(self.rezervace_id)
                if ok:
                    self.status.setText("Rezervace byla odstraněna.")
                    if self.hlavni_okno:
                        self.hlavni_okno.nacti_rezervace()
                    self.close()
                else:
                    self.status.setText("Chyba při odstraňování rezervace.")
            else:
                self.status.setText("Odstranění rezervace zrušeno.")
        else:
            self.status.setText("Žádná rezervace k odstranění.")

    def uloz(self):
        pacient_jmeno = self.pacient_jmeno_input.text()
        pacient_druh = self.pacient_druh_input.text()
        majitel_pacienta = self.majitel_input.text()
        majitel_kontakt = self.kontakt_majitel_input.text()
        doktor = self.doktor_input.currentText()
        note = self.note_input.toPlainText()
        dt = self.cas_input.dateTime()
        cas = dt.toString("yyyy-MM-dd HH:mm")
        mistnost = self.mistnost_input.currentText()
        max_cas = QTime(19, 40)
        min_cas = QTime(8, 0)

        if not pacient_jmeno:
            self.status.setText("Vyplňte jmeno pacienta.")
        elif not pacient_druh:
            self.status.setText("Vyplňte druh pacienta.")
        elif not majitel_pacienta:
            self.status.setText("Vyplňte příjmení majitele pacienta.")
        elif doktor == "!---Vyberte doktora---!":
            self.status.setText("Vybrat doktora.")
        elif mistnost == "!---Vyberte ordinaci---!":
            self.status.setText("Vybrat ordinaci.")
        elif dt.time() > max_cas or dt.time() < min_cas:
            self.status.setText(f"Zadán špatný čas rezervace ({dt.time().hour():02d}:{dt.time().minute():02d}).")
        else:
            if self.rezervace_id:
                # Úprava existující rezervace
                from controllers.rezervace_controller import aktualizuj_rezervaci
                ok = aktualizuj_rezervaci(
                    self.rezervace_id, pacient_jmeno, pacient_druh, majitel_pacienta,
                    majitel_kontakt, doktor, note, cas, mistnost
                )
                if ok:
                    self.status.setText("Rezervace byla upravena.")
                    if self.hlavni_okno:
                        self.hlavni_okno.nacti_rezervace()
                    self.close()
                else:
                    self.status.setText("Chyba při úpravě rezervace.")
            else:
                # Nová rezervace
                if uloz_rezervaci(pacient_jmeno, pacient_druh, majitel_pacienta, majitel_kontakt, doktor, note, cas, mistnost):
                    self.status.setText("Rezervace byla uložena.")
                    if self.hlavni_okno:
                        self.hlavni_okno.nacti_rezervace()
                    self.close()
                else:
                    self.status.setText("Chyba při ukládání.")

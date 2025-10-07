# views/formular_rezervace.py
from PySide6.QtWidgets import QWidget, QHBoxLayout, QLineEdit, QPushButton, QLabel, QFormLayout, QComboBox, QTextEdit, QDateTimeEdit, QMessageBox, QCheckBox
from PySide6.QtCore import QDateTime, QTime
from controllers.rezervace_controller import uloz_rezervaci, odstran_rezervaci_z_db, aktualizuj_rezervaci, kontrola_prekryvani_rezervaci
from models.databaze import get_doktori, get_ordinace
from controllers.data import basic_style
from models.doktori import time_anchores



class FormularRezervace(QWidget):
    def __init__(self, hlavni_okno=None, rezervace_data=None, predvyplneny_cas=None, predvyplnena_ordinace=None, predvyplneny_doktor=None):
        super().__init__(parent=hlavni_okno)  # Nastavit parent
        self.setWindowTitle("Nová rezervace" if rezervace_data is None else "Úprava rezervace")
        
        # Nastavit window flags aby se choval jako samostatné okno
        from PySide6.QtCore import Qt
        self.setWindowFlags(Qt.Window | Qt.WindowCloseButtonHint | Qt.WindowMinimizeButtonHint)
        
        self.rezervace_id = rezervace_data[1] if rezervace_data else None
        self.hlavni_okno = hlavni_okno
        self.predvyplneny_doktor = predvyplneny_doktor
        self.rezervace_data = rezervace_data
        self.setStyleSheet(basic_style)

        self.layout = QFormLayout()

        self.pacient_problem = QLineEdit()
        self.pacient_druh_input = QLineEdit()
        self.majitel_input = QLineEdit()
        self.kontakt_majitel_input = QLineEdit()
        self.doktor_input = QComboBox()
        self.druhy_doktor_input = QComboBox()
        self.doktor_input.addItem("!---Vyberte doktora---!")
        self.anestezie_checkbox = QCheckBox()
        self.druhy_doktor_input.addItem("!---Vyberte druhého doktora---!")
        self.doktor_input.addItems(self.get_doctors())
        # Signal pro aktualizaci druhého doktora při změně prvního
        self.doktor_input.currentTextChanged.connect(self.aktualizuj_druhy_doktor)
        # Inicializace seznamu druhých doktorů
        self.aktualizuj_druhy_doktor()

        self.cas_input = QDateTimeEdit()
        self.cas_input.setCalendarPopup(True)
        self.cas_input.setDisplayFormat("dd-MM-yyyy HH:mm")
        self.cas_input.setDateTime(QDateTime.currentDateTime())

        # Rozdělení na datum a čas
        self.datum_input = QDateTimeEdit()
        self.datum_input.setCalendarPopup(True)
        self.datum_input.setDisplayFormat("dd-MM-yyyy")
        self.datum_input.setDate(QDateTime.currentDateTime().date())

        self.cas_od_input = QComboBox()
        self.cas_od_input.addItems(time_anchores)
        # Nastavení aktuálního času jako výchozí
        current_time = QDateTime.currentDateTime().time().toString("HH:mm")
        if current_time in time_anchores:
            self.cas_od_input.setCurrentText(current_time)
        else:
            # Najít nejbližší vyšší čas
            for time_anchor in time_anchores:
                if QTime.fromString(time_anchor, "HH:mm") >= QDateTime.currentDateTime().time():
                    self.cas_od_input.setCurrentText(time_anchor)
                    break

        # Signal pro aktualizaci délky rezervace při změně času od
        self.cas_od_input.currentTextChanged.connect(self.aktualizuj_delku_rezervace)

        self.note_input = QTextEdit()
        self.mistnost_input = QComboBox()
        self.mistnost_input.addItem("!---Vyberte ordinaci---!")
        self.delka_rezervace_input = QComboBox()
        self.mistnost_input.addItems(self.get_ordinace_list())
        

        # Předvyplnění dat pokud jsou k dispozici
        if rezervace_data:
          # Předpoklad: rezervace_data = (cas, id, doktor, doktor_color, pacient, majitel, kontakt, druh, mistnost, poznamka, cas_od, cas_do, anestezie, druhy_doktor, druhy_doktor_barva)
          # Ošetření None hodnot pro text inputy
          self.pacient_problem.setText(rezervace_data[4] if rezervace_data[4] is not None else "")
          self.pacient_druh_input.setText(rezervace_data[7] if rezervace_data[7] is not None else "")
          self.majitel_input.setText(rezervace_data[5] if rezervace_data[5] is not None else "")
          self.kontakt_majitel_input.setText(rezervace_data[6] if rezervace_data[6] is not None else "")
          
          # Kontrola a nastavení doktora
          doktor_z_rezervace = rezervace_data[2]
          idx = -1  # Inicializace indexu
          
          # Zkontroluj, zda doktor není None (rezervace bez doktora)
          if doktor_z_rezervace is not None:
              doktor_normalized = ' '.join(doktor_z_rezervace.split())  # Normalizace mezer
              
              # Pokusíme se najít přesnou shodu
              idx = self.doktor_input.findText(doktor_z_rezervace)
              
              # Pokud nenajdeme přesnou shodu, zkusíme normalizovanou shodu
              if idx == -1:
                  for i in range(self.doktor_input.count()):
                      doctor_name = self.doktor_input.itemText(i)
                      doctor_name_normalized = ' '.join(doctor_name.split())
                      if doctor_name_normalized.lower() == doktor_normalized.lower():
                          idx = i
                          break
          
          # Nastaví doktora pokud byl nalezen, jinak zůstane prázdný (pro rezervace bez doktora)
          if idx != -1:
              self.doktor_input.setCurrentIndex(idx)
          
          # Předvyplnění anestézie (index 12)
          if len(rezervace_data) > 12 and rezervace_data[12] is not None:
              self.anestezie_checkbox.setChecked(bool(rezervace_data[12]))
          
          # Předvyplnění druhého doktora (index 13) - musí být až po nastavení prvního doktora
          if len(rezervace_data) > 13 and rezervace_data[13]:
              # Najít druhého doktora v seznamu
              druhy_doktor_idx = self.druhy_doktor_input.findText(rezervace_data[13])
              if druhy_doktor_idx != -1:
                  self.druhy_doktor_input.setCurrentIndex(druhy_doktor_idx)
          
          # Ošetření poznámky - může být None
          poznamka = rezervace_data[9] if rezervace_data[9] is not None else ""
          self.note_input.setPlainText(poznamka)
          
          # Handle both datetime object (PostgreSQL) and string (SQLite) formats for rezervace_data[0]
          if hasattr(rezervace_data[0], 'strftime'):  # datetime object
              datum_str = rezervace_data[0].strftime("%Y-%m-%d")
          else:
              datum_str = str(rezervace_data[0])
          
          dt = QDateTime.fromString(f"{datum_str} {rezervace_data[10]}", "yyyy-MM-dd HH:mm")
          if dt.isValid():
              # self.cas_input.setDateTime(dt)
              self.datum_input.setDate(dt.date())
              self.cas_od_input.setCurrentText(dt.time().toString("HH:mm"))
              # Naplnění možností pro čas do na základě času od
              self.aktualizuj_delku_rezervace()
          # Nastavení délky rezervace (času do) - cas_do je na indexu 11
          if len(rezervace_data) > 11 and rezervace_data[11]:
              self.delka_rezervace_input.setCurrentText(rezervace_data[11])    
          idx2 = self.mistnost_input.findText(rezervace_data[8])
          if idx2 != -1:
              self.mistnost_input.setCurrentIndex(idx2)
                
                
        else:
            # Předvyplnění z dvojkliku na prázdný řádek
            if predvyplneny_cas:
                dt = QDateTime.fromString(predvyplneny_cas, "yyyy-MM-dd HH:mm")
                if dt.isValid():
                    # self.cas_input.setDateTime(dt)
                    self.datum_input.setDate(dt.date())
                    self.cas_od_input.setCurrentText(dt.time().toString("HH:mm"))
                    self.delka_rezervace_input.setCurrentText(dt.time().toString("HH:mm"))
            if predvyplnena_ordinace:
                idx = self.mistnost_input.findText(predvyplnena_ordinace)
                if idx != -1:
                    self.mistnost_input.setCurrentIndex(idx)
            if predvyplneny_doktor:
                idx = self.doktor_input.findText(predvyplneny_doktor)
                if idx != -1:
                    self.doktor_input.setCurrentIndex(idx)
              

        # Časové kotvy pro délku rezervace
        # self.delka_rezervace_input.addItems(self.reservation_length())
        
        self.layout.addRow("Příjmení majitele:", self.majitel_input)
        self.layout.addRow("Co trápí pacienta:", self.pacient_problem)
        self.layout.addRow("Druh pacienta:", self.pacient_druh_input)
        self.layout.addRow("Kontakt majitele (nemusí být):", self.kontakt_majitel_input)
        self.layout.addRow("Doktor:", self.doktor_input)
        self.layout.addRow("Anestézie (nemusí být):", self.anestezie_checkbox)
        self.layout.addRow("Druhý doktor (nemusí být):", self.druhy_doktor_input) if hasattr(self, 'druhy_doktor_input') else None
        self.layout.addRow("Poznámka (nemusí být):", self.note_input)
        self.layout.addRow("Datum:", self.datum_input)
        self.layout.addRow("Čas od:", self.vytvor_cas_layout())
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
        # Handle both dictionary (PostgreSQL) and tuple (SQLite) formats
        if doktori and isinstance(doktori[0], dict):
            # PostgreSQL format - use dictionary keys
            return [' '.join(f"{i['jmeno']} {i['prijmeni']}".split()) for i in doktori]
        else:
            # SQLite format - use index access
            return [' '.join(f"{i[1]} {i[2]}".split()) for i in doktori]
          
    def aktualizuj_druhy_doktor(self):
        """Aktualizuje seznam druhých doktorů bez vybraného prvního doktora"""
        vybrany_prvni_doktor = self.doktor_input.currentText()
        
        # Vymazat současný obsah
        self.druhy_doktor_input.clear()
        self.druhy_doktor_input.addItem("!---Vyberte druhého doktora---!")
        
        # Přidat všechny doktory kromě vybraného prvního
        vsichni_doktori = self.get_doctors()
        for doktor in vsichni_doktori:
            if doktor != vybrany_prvni_doktor and vybrany_prvni_doktor != "!---Vyberte doktora---!":
                self.druhy_doktor_input.addItem(doktor)

    def get_ordinace_list(self):
        ordinace = get_ordinace()
        # Handle both dictionary (PostgreSQL) and tuple (SQLite) formats
        if ordinace and isinstance(ordinace[0], dict):
            # PostgreSQL format - use dictionary keys
            return [f"{i['nazev']}" for i in ordinace]
        else:
            # SQLite format - use index access
            return [f"{i[1]}" for i in ordinace]
    
    def vytvor_cas_layout(self):
        """Vytvoří layout pro čas od-do"""
        cas_widget = QWidget()
        cas_layout = QHBoxLayout(cas_widget)
        cas_layout.setContentsMargins(0, 0, 0, 0)
        cas_layout.setSpacing(6)  # Minimální mezera mezi widgety
        
        # Nastavení minimální šířky pro ComboBox widgety
        self.cas_od_input.setMinimumWidth(80)
        self.delka_rezervace_input.setMinimumWidth(80)
        
        cas_layout.addWidget(self.cas_od_input)
        cas_layout.addWidget(QLabel("do: "))  # Kratší oddělovač
        cas_layout.addWidget(self.delka_rezervace_input)
        cas_layout.addStretch()  # Přidá volné místo na konec
        
        return cas_widget

    def aktualizuj_delku_rezervace(self):
        """Aktualizuje možnosti délky rezervace na základě vybraného času od"""
        cas_od = self.cas_od_input.currentText()
        self.delka_rezervace_input.clear()
        self.delka_rezervace_input.addItems(self.reservation_length_from_time(cas_od))

    def reservation_length_from_time(self, start_time):
        """Vrátí možné časy do na základě času od"""
        try:
            start_index = time_anchores.index(start_time)
            return time_anchores[start_index:]
        except ValueError:
            return time_anchores[1:]  # Fallback

    def reservation_length(self):
        # start = self.cas_input.dateTime().toString('HH:mm')
        start = self.cas_od_input.currentText() if hasattr(self, 'cas_od_input') else time_anchores[0]
        return self.reservation_length_from_time(start)
    
    
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
        pacient_problem = self.pacient_problem.text().strip()
        pacient_druh = self.pacient_druh_input.text().strip()
        majitel_pacienta = self.majitel_input.text().strip()
        majitel_kontakt = self.kontakt_majitel_input.text().strip()
        doktor = self.doktor_input.currentText() if self.doktor_input.currentText() != "!---Vyberte doktora---!" else None
        anestezie = self.anestezie_checkbox.isChecked()
        druhy_doktor = self.druhy_doktor_input.currentText() if self.druhy_doktor_input.currentText() != "!---Vyberte druhého doktora---!" else None
        note = self.note_input.toPlainText().strip()
        print(f"Anestezie: {anestezie}, Druhý doktor: {druhy_doktor}")
        
        # Sestavení datetime z datumu a času
        datum = self.datum_input.date().toString("yyyy-MM-dd")
        cas_od = self.cas_od_input.currentText()
        cas_do = self.delka_rezervace_input.currentText()

        mistnost = self.mistnost_input.currentText()
        max_cas = QTime(19, 40)
        min_cas = QTime(8, 0)

        # Kontrola času
        selected_time = QTime.fromString(cas_od, "HH:mm")

        if not pacient_problem:
            self.status.setText("Vyplňte problém pacienta, případně jméno.")
        elif not pacient_druh:
            self.status.setText("Vyplňte druh pacienta.")
        elif not majitel_pacienta:
            self.status.setText("Vyplňte příjmení majitele pacienta.")
        elif mistnost == "!---Vyberte ordinaci---!":
            self.status.setText("Vybrat ordinaci.")
        elif selected_time > max_cas or selected_time < min_cas:
            self.status.setText(f"Zadán špatný čas rezervace ({selected_time.toString('HH:mm')}).")
        elif cas_od in ["12:00", "16:45"]:
            self.status.setText(f"V pauze nelze rezervovat ({selected_time.toString('HH:mm')}).")
        else:
            # Kontrola překrývání rezervací
            prekryva, chyba_zprava = kontrola_prekryvani_rezervaci(
                datum, cas_od, cas_do, mistnost, self.rezervace_id
            )
            
            if prekryva:
                self.status.setText(f"{chyba_zprava}")
                return
            
            if self.rezervace_id:
                # Úprava existující rezervace
                ok = aktualizuj_rezervaci(
                    self.rezervace_id, pacient_problem, pacient_druh, majitel_pacienta,
                    majitel_kontakt, doktor, anestezie, druhy_doktor, note, datum, cas_od, cas_do, mistnost
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
                if uloz_rezervaci(pacient_problem, pacient_druh, majitel_pacienta, majitel_kontakt, doktor, anestezie, druhy_doktor, note, datum, cas_od, cas_do, mistnost):
                    self.status.setText("Rezervace byla uložena.")
                    if self.hlavni_okno:
                        self.hlavni_okno.nacti_rezervace()
                    self.close()
                else:
                    self.status.setText("Chyba při ukládání.")
    
    def closeEvent(self, event):
        """Obsluha zavření formuláře"""
        print(f"🔴 Zavírám FormularRezervace")
        # Odregistruj se z hlavního okna pokud je nastaveno
        if self.hlavni_okno and hasattr(self.hlavni_okno, 'unregister_dialog'):
            self.hlavni_okno.unregister_dialog(self)
        event.accept()

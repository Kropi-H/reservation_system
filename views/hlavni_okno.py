from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QTextEdit, QDateEdit, QHBoxLayout, QTabWidget, QTableWidget, QTableWidgetItem
from PySide6.QtCore import QDate
from PySide6.QtGui import QColor
from views.formular_rezervace import FormularRezervace
from models.rezervace import ziskej_rezervace_dne
from datetime import datetime, timedelta
from models.databaze import get_ordinace
from views.formular_rezervace import FormularRezervace
from controllers.data import table_grey_strip, vaccination_color, pause_color


def get_ordinace_list():
        ordinace = get_ordinace()
        return [ f"{i[1]}" for i in ordinace]

ordinace = get_ordinace_list()

class HlavniOkno(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Veterinární rezervační systém")
        layout = QVBoxLayout()
        self.setMinimumWidth(1300)
        self.setMinimumHeight(900)

        # Výběr dne
        radek = QHBoxLayout()
        self.btn_predchozi = QPushButton("<")
        self.btn_predchozi.clicked.connect(self.predchozi_den)
        self.btn_nasledujici = QPushButton(">")
        self.btn_nasledujici.clicked.connect(self.nasledujici_den)

        self.kalendar = QDateEdit()
        self.kalendar.setDate(QDate.currentDate())
        self.kalendar.setCalendarPopup(True)
        self.kalendar.dateChanged.connect(self.nacti_rezervace)

        radek.addWidget(self.btn_predchozi)
        radek.addWidget(self.kalendar)
        radek.addWidget(self.btn_nasledujici)
        layout.addLayout(radek)

        # Tlačítko pro novou rezervaci
        self.btn_nova = QPushButton("Nová rezervace")
        self.btn_nova.clicked.connect(self.otevri_formular)
        layout.addWidget(self.btn_nova)

        # Záložky pro jednotlivé ordinace
        self.tabulky = {} # mistnost -> QTableWidget
        self.ordinace_layout = QHBoxLayout()  
        
        for mistnost in ordinace:
            tabulka = QTableWidget()
            tabulka.setColumnCount(2)
            # tabulka.setHorizontalHeaderLabels(["ČAS", "MAJITELl"])
            tabulka.setColumnWidth(0, 50) # Čas
            # tabulka.setColumnWidth(1, 70) # Objednán na
            # tabulka.setColumnWidth(2, 200) # Doktor
            # tabulka.setColumnWidth(3, 200) # Pacient
            # tabulka.setColumnWidth(4, 300) # Poznámka
            tabulka.setColumnWidth(1, 200) # Majitel 

            # Skrytí sloupce s čísly řádků
            tabulka.verticalHeader().setVisible(False)
            
            # Nastavení stylu pro záhlaví
            tabulka.horizontalHeader().setStyleSheet("""
              QHeaderView::section {
                  background-color: #9ee0fc;
                  color: #d8d8d8;
                  font-style: uppercase;
                  font-weight: bold;
                  font-size: 14px;
                  color: black;
              }
            """)

            self.ordinace_layout.addWidget(tabulka)
            self.tabulky[mistnost] = tabulka

        layout.addLayout(self.ordinace_layout)
        self.setLayout(layout)
        self.nacti_rezervace()

    def otevri_formular(self):
        self.formular = FormularRezervace(self)
        self.formular.show()

    def predchozi_den(self):
        self.kalendar.setDate(self.kalendar.date().addDays(-1))

    def nasledujici_den(self):
        self.kalendar.setDate(self.kalendar.date().addDays(1))

    def nacti_rezervace(self):
      datum = self.kalendar.date().toPython()
      rezervace = ziskej_rezervace_dne(datum.strftime("%Y-%m-%d"))

      # Vymaž všechny tabulky
      for tabulka in self.tabulky.values():
          tabulka.setRowCount(0)

      # Zmapuj rezervace podle ordinace
      mapovane = {i: [] for i in ordinace}
      for r in rezervace:
          cas = datetime.strptime(r[0], "%Y-%m-%d %H:%M")
          doktor = r[1]
          doktor_color = r[2]
          pacient = r[3]
          majitel = r[4]
          kontakt = r[5]
          druh = r[6]
          mistnost = r[7]
          poznamka = r[8]

          if mistnost in mapovane:
              mapovane[mistnost].append((cas, doktor, doktor_color, pacient, majitel, kontakt, druh, poznamka))
          #print("Mapované rezervace:", mapovane)

      # Vlož data do tabulek
      for mistnost, tabulka in self.tabulky.items():
          tabulka.setHorizontalHeaderLabels(["ČAS", f"{mistnost}"]) # Set the name of the columne (ordinace)
          index = 0
          cas = datetime.combine(datum, datetime.strptime("08:00", "%H:%M").time())
          end = datetime.combine(datum, datetime.strptime("20:00", "%H:%M").time())

          while cas <= end:
            # Nastav slot podle času
              pause_time = False
              #slot = timedelta(minutes=20)
              if cas.time() >= datetime.strptime("09:00", "%H:%M").time() and cas.time() <= datetime.strptime("09:45", "%H:%M").time():
                  slot = timedelta(minutes=15)
                  vaccination_time = True
              elif cas.time() >= datetime.strptime("12:00", "%H:%M").time() and cas.time() < datetime.strptime("12:30", "%H:%M").time():
                slot = timedelta(minutes=30)
                pause_time = True
              elif cas.time() >= datetime.strptime("12:30", "%H:%M").time() and cas.time() < datetime.strptime("12:40", "%H:%M").time():
                slot = timedelta(minutes=10)
                
              elif cas.time() == datetime.strptime("12:40", "%H:%M").time():
                slot = timedelta(minutes=20)
                cas = datetime.combine(datum, datetime.strptime("12:40", "%H:%M").time())
                
              elif cas.time() >= datetime.strptime("16:00", "%H:%M").time() and cas.time() <= datetime.strptime("16:30", "%H:%M").time():
                  slot = timedelta(minutes=15)
                  vaccination_time = True
                  
                  
              elif cas.time() == datetime.strptime("16:45", "%H:%M").time():
                slot = timedelta(minutes=35)
                vaccination_time = False
                pause_time = True
                
              elif cas.time() >= datetime.strptime("17:20", "%H:%M").time():
                  slot = timedelta(minutes=20)
                  vaccination_time = False  
                
              else:
                  slot = timedelta(minutes=20)
                  vaccination_time = False
                  
              cas_str = cas.strftime("%H:%M")
              tabulka.insertRow(index)

              # Debug: Výpis všech porovnání
              '''
              for rez in mapovane[mistnost]:
                  print(f"Porovnávám: {rez[0].strftime('%H:%M')} == {cas_str}")
              '''
              # Najdi odpovídající rezervaci pro aktuální čas
              rezervace_pro_cas = [
                rez for rez in mapovane[mistnost] if rez[0] >= cas and rez[0] < cas + slot
              ]

              #print(f"Vkládám do tabulky {mistnost}: {rezervace_pro_cas}")
              # Vlož data do jednotlivých sloupců
              if rezervace_pro_cas:  # Čas
                for rez in rezervace_pro_cas:
                  # tabulka.insertRow(index)
                  tabulka.setItem(index, 0, QTableWidgetItem(cas_str))  # Čas
                  doktor_item = QTableWidgetItem(f"{rez[4]} {'kontakt: ' + rez[5] if rez[5] else ''}")  # Doktor
                  tabulka.setItem(index, 1, doktor_item)
                  
                  # Nastavení světle šedého pozadí pro celý řádek
                  if index % 2 == 0:  # Sudý řádek
                      for col in range(2):  # Pro všechny sloupce
                          item = tabulka.item(index, col)
                          if item and vaccination_time == True:  # Pokud buňka existuje
                              item.setBackground(QColor(vaccination_color))  # Vakcinační pozadí
                          else:  # Lichý řádek
                              item.setBackground(QColor(table_grey_strip))  # Světle šedé pozadí

                  # Nastavení světle modrého pozadí pro buňku "DOKTOR", pokud obsahuje jméno
                  if rez[1]:  # Pokud je jméno doktora vyplněné
                      doktor_item.setBackground(QColor(rez[2].strip()))  # Pozadí doktora  
                  
                  
                  index += 1

              else:
                  # Pokud není rezervace, ponech prázdné buňky
                  tabulka.setItem(index, 0, QTableWidgetItem(cas_str))
                  tabulka.setItem(index, 1, QTableWidgetItem(""))

                  # Nastavení světle šedého pozadí pro každý druhý řádek vaccination_color
                  # Sudý řádek
                  for col in range(2):  # Pro všechny sloupce
                    if index % 2 == 0:  # Pokud je vakcinační čas
                      if vaccination_time == True:
                       tabulka.item(index, 0).setBackground(QColor(vaccination_color))
                       tabulka.item(index, 1).setBackground(QColor(table_grey_strip))
                      elif pause_time == True:
                        tabulka.item(index, col).setBackground(QColor(pause_color))
                      else:
                        tabulka.item(index, col).setBackground(QColor(table_grey_strip))
                    elif pause_time == True:
                      tabulka.item(index, col).setBackground(QColor(pause_color)) # Pokud je pauza
                    elif vaccination_time == True:
                      tabulka.item(index, 0).setBackground(QColor(vaccination_color))
                                                            
                  index += 1
                  
              cas += slot
              
      #print("Rezervace načtené z databáze:", rezervace)
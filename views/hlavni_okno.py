from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QTextEdit, QDateEdit, QHBoxLayout, QTabWidget, QTableWidget, QTableWidgetItem
from PySide6.QtCore import QDate, QLocale
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
        self.showMaximized()  # Přidat tento řádek pro maximalizaci okna při startu     
        
        # Styl pro všechny tabulky v tomto okně
        self.setStyleSheet("""
            QTableWidget {
                background-color: #fafdff;
                font-size: 15px;
                color: #222;
                gridline-color: #b2d7ef;
                selection-background-color: #cceeff;
                selection-color: #000;
            }
            QTableWidget::item {
                padding: 6px;
            }
            QHeaderView::section {
                background-color: #9ee0fc;
                color: black;
                font-weight: bold;
                font-size: 14px;
            }
            QToolTip{ 
            background-color: #e6f7ff; 
            color: #222; border: 
            1px solid #009688; 
            font-size: 14px; }
        """)   
        

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
        self.kalendar.dateChanged.connect(self.aktualizuj_format_kalendare)
        
        # Nastav formát při startu
        self.aktualizuj_format_kalendare(self.kalendar.date())

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
            tabulka.setColumnCount(2) # Počet sloupců
            tabulka.setColumnWidth(0, 50) # Čas
            tabulka.horizontalHeader().setStretchLastSection(True)  # Řádek rezervace v maximální šířce

            # Skrytí sloupce s čísly řádků
            tabulka.verticalHeader().setVisible(False)
            
            # Připojení signálu pro dvojklik
            tabulka.cellDoubleClicked.connect(lambda row, col, m=mistnost: self.zpracuj_dvojklik(m, row, col))


            self.ordinace_layout.addWidget(tabulka)
            self.tabulky[mistnost] = tabulka

        layout.addLayout(self.ordinace_layout)
        self.setLayout(layout)
        self.nacti_rezervace()
    
    def zpracuj_dvojklik(self, mistnost, row, col):
      tabulka = self.tabulky[mistnost]
      cas_item = tabulka.item(row, 0)
      data_item = tabulka.item(row, 1)
      cas_str = cas_item.text() if cas_item else ""
      data_str = data_item.text() if data_item else ""

      if not data_str.strip():
          # Předvyplň čas a ordinaci
          datum = self.kalendar.date().toPython()
          if cas_str:
              dt_str = f"{datum.strftime('%Y-%m-%d')} {cas_str}"
          else:
              dt_str = None
          self.formular = FormularRezervace(self, predvyplneny_cas=dt_str, predvyplnena_ordinace=mistnost)
          self.formular.show()
      else:
          datum = self.kalendar.date().toPython()
          rezervace = ziskej_rezervace_dne(datum.strftime("%Y-%m-%d"))
          for r in rezervace:
              if r[7] == mistnost and r[0].endswith(cas_str):
                  self.formular = FormularRezervace(self, rezervace_data=r)
                  self.formular.show()
                  break    

    def aktualizuj_format_kalendare(self, datum):
        locale = QLocale(QLocale.Czech)
        den = locale.dayName(datum.dayOfWeek(), QLocale.LongFormat)
        datum_str = datum.toString("d.M.yyyy")
        self.kalendar.setDisplayFormat(f"'{den} 'd.M.yyyy")

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
                  # Přidejte tooltip s detaily rezervace
                  tooltip_text = (
                      f"<b>Čas:</b> {cas_str}<br>"
                      f"<b>Pacient:</b> {rez[3]}<br>"
                      f"<b>Majitel:</b> {rez[4]}<br>"
                      f"<b>Kontakt:</b> {rez[5]}<br>"
                      f"<b>Druh:</b> {rez[6]}<br>"
                      f"<b>Doktor:</b> {rez[1]}<br>"
                      f"<b>Poznámka:</b> {rez[7]}"
                  )
                  doktor_item.setToolTip(tooltip_text)
                  tabulka.setItem(index, 1, doktor_item)
                  
                  # Nastavení světle šedého pozadí pro celý řádek
                  if index % 2 == 0:  # Sudý řádek
                      for col in range(2):  # Pro všechny sloupce
                          if vaccination_time == True:  # Pokud buňka existuje
                              tabulka.item(index, 0).setBackground(QColor(vaccination_color))  # Vakcinační pozadí
                          else:  # Lichý řádek
                              tabulka.item(index, 0).setBackground(QColor(table_grey_strip))  # Světle šedé pozadí

                  # Nastavení světle modrého pozadí pro buňku "DOKTOR", pokud obsahuje jméno
                  if rez[1]:  # Pokud je jméno doktora vyplněné
                      doktor_item.setBackground(QColor(rez[2].strip()))  # Pozadí doktora
                      if vaccination_time == True:
                          tabulka.item(index, 0).setBackground(QColor(vaccination_color)) 
                  
                  
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
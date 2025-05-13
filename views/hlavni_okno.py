from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QTextEdit, QDateEdit, QHBoxLayout, QTabWidget, QTableWidget, QTableWidgetItem
from PySide6.QtCore import QDate
from PySide6.QtGui import QColor
from views.formular_rezervace import FormularRezervace
from models.rezervace import ziskej_rezervace_dne
from datetime import datetime, timedelta
from models.databaze import get_ordinace
from views.formular_rezervace import FormularRezervace
from controllers.data import table_grey_strip


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
        self.tab_widget = QTabWidget()
        self.tabulky = {}  # mistnost -> QTableWidget

        for mistnost in ordinace:
            tabulka = QTableWidget()
            tabulka.setColumnCount(6)
            tabulka.setHorizontalHeaderLabels(["ČAS", "ČAS OBJ.:", "DOKTOR", "PACIENT", "POZNÁMKA", "MAJITEL"])
            tabulka.setColumnWidth(0, 50) # Čas
            tabulka.setColumnWidth(1, 70) # Objednán na
            tabulka.setColumnWidth(2, 200) # Doktor
            tabulka.setColumnWidth(3, 200) # Pacient
            tabulka.setColumnWidth(4, 300) # Poznámka
            tabulka.setColumnWidth(5, 200) # Majitel 

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

            self.tab_widget.addTab(tabulka, mistnost.upper())
            self.tabulky[mistnost] = tabulka


        # Nastavení stylu pro celý QTabBar
        self.tab_widget.tabBar().setStyleSheet("""
            QTabBar::tab {
                font-weight: bold;
                font-size: 14px;
                padding: 2px 5px;
                border: 1px solid  #d8d8d8;
                color: white;
            }
            QTabBar::tab:selected {
                background-color: #054e90;  /* Barva vybrané záložky */
            }
            QTabBar::tab:!selected {
                color: black;
                background-color: white;  /* Barva nevybraných záložek */
            }
        """)    
    
        layout.addWidget(self.tab_widget)
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
          #print("Načtený čas:", cas)
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
          index = 0
          cas = datetime.combine(datum, datetime.strptime("08:00", "%H:%M").time())
          end = datetime.combine(datum, datetime.strptime("20:00", "%H:%M").time())
          slot = timedelta(minutes=20)

          while cas < end:
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
                  tabulka.insertRow(index)
                  tabulka.setItem(index, 0, QTableWidgetItem(cas_str))  # Čas
                  tabulka.setItem(index, 1, QTableWidgetItem(rez[0].strftime("%H:%M")))  # Rezervační čas
                  doktor_item = QTableWidgetItem(rez[1])  # Doktor
                  tabulka.setItem(index, 2, doktor_item)
                  #doktor_item.setBackground(QColor("#9ee0fc"))
                  tabulka.setItem(index, 3, QTableWidgetItem(f"{rez[6]}: {rez[3]}"))  # Pacient
                  tabulka.setItem(index, 4, QTableWidgetItem(rez[7]))  # Poznámka
                  tabulka.setItem(index, 5, QTableWidgetItem(f"{rez[4]} {'kontakt: ' + rez[5] if rez[5] else ''}"))  # Majitel
                  
                  # Nastavení světle šedého pozadí pro celý řádek
                  if index % 2 == 0:  # Sudý řádek
                      for col in range(6):  # Pro všechny sloupce
                          item = tabulka.item(index, col)
                          if item:  # Pokud buňka existuje
                              item.setBackground(QColor(table_grey_strip))  # Světle šedé pozadí

                  # Nastavení světle modrého pozadí pro buňku "DOKTOR", pokud obsahuje jméno
                  if rez[1]:  # Pokud je jméno doktora vyplněné
                      doktor_item.setBackground(QColor(rez[2].strip()))  # Pozadí doktora  
                  
                  index += 1

              else:
                  # Pokud není rezervace, ponech prázdné buňky
                  tabulka.setItem(index, 0, QTableWidgetItem(cas_str))
                  tabulka.setItem(index, 1, QTableWidgetItem(""))
                  tabulka.setItem(index, 2, QTableWidgetItem(""))
                  tabulka.setItem(index, 3, QTableWidgetItem(""))
                  tabulka.setItem(index, 4, QTableWidgetItem(""))
                  tabulka.setItem(index, 5, QTableWidgetItem(""))

                  # Nastavení světle šedého pozadí pro každý druhý řádek
                  if index % 2 == 0:  # Sudý řádek
                    for col in range(6):  # Pro všechny sloupce
                        tabulka.item(index, col).setBackground(QColor(table_grey_strip))
                                                              
                  index += 1
              cas += slot
              
      #print("Rezervace načtené z databáze:", rezervace)
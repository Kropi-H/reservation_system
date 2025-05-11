from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QTextEdit, QDateEdit, QHBoxLayout, QTabWidget, QTableWidget, QTableWidgetItem
from PySide6.QtCore import QDate
from views.formular_rezervace import FormularRezervace
from models.rezervace import ziskej_rezervace_dne
from datetime import datetime, timedelta
from models.databaze import get_ordinace
from views.formular_rezervace import FormularRezervace

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
            tabulka.setHorizontalHeaderLabels(["Čas", "Objednán na:", "Doktor", "Pacient", "Majitel", "Poznámka"])
            # tabulka.setColumnWidth(1, 500)
            self.tab_widget.addTab(tabulka, mistnost)
            self.tabulky[mistnost] = tabulka

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
          pacient = r[2]
          majitel = r[3]
          mistnost = r[4]
          poznamka = r[5]

          if mistnost in mapovane:
              mapovane[mistnost].append((cas, doktor, pacient, majitel, poznamka))
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
              rezervace_pro_cas = next(
                (rez for rez in mapovane[mistnost] if rez[0] >= cas and rez[0] < cas + slot),
                None,
              )

              #print(f"Vkládám do tabulky {mistnost}: {rezervace_pro_cas}")
              # Vlož data do jednotlivých sloupců
              tabulka.setItem(index, 0, QTableWidgetItem(cas_str))  # Čas
              if rezervace_pro_cas:
                  tabulka.setItem(index, 1, QTableWidgetItem(rezervace_pro_cas[0].strftime('%H:%M')))  # cas
                  tabulka.setItem(index, 2, QTableWidgetItem(rezervace_pro_cas[1]))  # Doktor
                  tabulka.setItem(index, 3, QTableWidgetItem(rezervace_pro_cas[2]))  # Pacient
                  tabulka.setItem(index, 4, QTableWidgetItem(rezervace_pro_cas[3]))  # Majitel
                  tabulka.setItem(index, 5, QTableWidgetItem(rezervace_pro_cas[4]))  # Poznámka

              else:
                  # Pokud není rezervace, ponech prázdné buňky
                  tabulka.setItem(index, 1, QTableWidgetItem(""))
                  tabulka.setItem(index, 2, QTableWidgetItem(""))
                  tabulka.setItem(index, 3, QTableWidgetItem(""))
                  tabulka.setItem(index, 4, QTableWidgetItem(""))

              cas += slot
              index += 1
      #print("Rezervace načtené z databáze:", rezervace)
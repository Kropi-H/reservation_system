from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QTextEdit, QDateEdit, QHBoxLayout, QTabWidget, QTableWidget, QTableWidgetItem
from PySide6.QtCore import QDate
from views.formular_rezervace import FormularRezervace
from models.rezervace import ziskej_rezervace_dne
from datetime import datetime, timedelta
from controllers.data import ordinace, doktori

# ORDINACE = ["Ordinace 1", "Ordinace 2", "Ordinace 3"]

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
            tabulka.setColumnCount(5)
            tabulka.setHorizontalHeaderLabels(["Čas", "Doktor", "Pacient", "Majitel", "Poznámka"])
            # tabulka.setColumnWidth(1, 500)
            self.tab_widget.addTab(tabulka, mistnost['nazev'])
            self.tabulky[mistnost["nazev"]] = tabulka

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

        # Zmapuj rezervace podle ordinace a času
        mapovane = {i["nazev"]: {} for i in ordinace}
        for r in rezervace:
            cas_dt = datetime.strptime(r[3], "%Y-%m-%d %H:%M")
            cas_str = cas_dt.strftime("%H:%M")
            mistnost = r[4]
            if mistnost in mapovane:
                mapovane[mistnost][cas_str] = f"{r[1]} / {r[2]}"

        start = datetime.combine(datum, datetime.strptime("08:00", "%H:%M").time())
        end = datetime.combine(datum, datetime.strptime("20:00", "%H:%M").time())
        slot = timedelta(minutes=30)

        for mistnost, tabulka in self.tabulky.items():
            index = 0
            cas = start
            while cas < end:
                cas_str = cas.strftime("%H:%M")
                tabulka.insertRow(index)
                tabulka.setItem(index, 0, QTableWidgetItem(cas_str))
                tabulka.setItem(index, 1, QTableWidgetItem(mapovane[mistnost].get(cas_str, "")))
                cas += slot
                index += 1

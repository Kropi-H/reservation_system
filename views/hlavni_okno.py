from PySide6.QtWidgets import (QWidget, QVBoxLayout, QPushButton, QLabel, 
                               QDateEdit, QHBoxLayout, QTableWidget, 
                               QTableWidgetItem, QMenuBar, QMenu, QMainWindow)
from PySide6.QtCore import QDate, QLocale, QTimer, Qt
from PySide6.QtGui import QColor, QPixmap, QAction
from views.formular_rezervace import FormularRezervace
from models.rezervace import ziskej_rezervace_dne
from datetime import datetime, timedelta
from models.databaze import get_ordinace
from models.doktori import vloz_ordinacni_cas
from views.login_dialog import LoginDialog
from controllers.data import table_grey_strip, vaccination_color, pause_color
from controllers.rezervace_controller import uloz_rezervaci
from models.databaze import get_doktori
from views.vyber_doktora_dialog import VyberDoktoraDialog
from views.planovani_ordinaci_dialog import PlanovaniOrdinaciDialog
import os

doktori = [f"{d[1]} {d[2]}" for d in get_doktori()]

def get_ordinace_list():
        ordinace = get_ordinace()
        return [ f"{i[1]}" for i in ordinace]

ordinace = get_ordinace_list()

class HlavniOkno(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Veterinární rezervační systém")
        layout = QVBoxLayout()
        self.showMaximized()  # Přidat tento řádek pro maximalizaci okna při startu     
        self.logged_in_user = None
        self.logged_in_user_role = None
        
        # --- MENU BAR ---
        self.menu_bar = QMenuBar(self)
        self.login_action = QAction("Přihlášení", self)
        self.login_action.triggered.connect(self.show_login_dialog)
        self.menu_bar.addAction(self.login_action)
        
        # Uživatel menu bude přidáváno/odebíráno dynamicky
        self.user_menu = None
        
            
        self.setMenuBar(self.menu_bar)  # Přidání menu bar do layoutu
        
        # --- STATUS BAR ---
        self.status_bar = self.statusBar()
        self.status_bar.showMessage("Nepřihlášen")
        
        # --- CENTRÁLNÍ WIDGET A LAYOUT ---
        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)
        
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
        

        # --- NOVÝ HORIZONTÁLNÍ LAYOUT PRO LOGO, DATUM, HODINY ---
        horni_radek = QHBoxLayout()

        # Logo vlevo
        self.logo_label = QLabel()
        logo_path = os.path.join(os.path.dirname(__file__), "../pictures/karakal_logo_grey.png")
        pixmap = QPixmap(logo_path)
        if not pixmap.isNull():
            self.logo_label.setPixmap(pixmap.scaledToHeight(48))
        else:
            self.logo_label.setText("Logo nenalezeno")
        horni_radek.addWidget(self.logo_label)

        # --- Střední část: tlačítka a kalendář ---
        stredni_widget = QWidget()
        stredni_layout = QHBoxLayout()
        stredni_layout.setContentsMargins(0, 0, 0, 0)
        stredni_layout.setSpacing(10)

        self.btn_predchozi = QPushButton("<")
        self.btn_predchozi.setFixedWidth(40)
        self.btn_predchozi.setStyleSheet("font-size: 18px;")
        self.btn_predchozi.clicked.connect(self.predchozi_den)

        self.kalendar = QDateEdit()
        self.kalendar.setDate(QDate.currentDate())
        self.kalendar.setCalendarPopup(True)
        self.kalendar.setStyleSheet("""
            QDateEdit {
                font-size: 22px;
                min-width: 160px;
                qproperty-alignment: AlignCenter;
                padding: 4px 10px;
            }
        """)
        self.kalendar.dateChanged.connect(self.nacti_rezervace)
        self.kalendar.dateChanged.connect(self.aktualizuj_format_kalendare)
        self.aktualizuj_format_kalendare(self.kalendar.date())

        self.btn_nasledujici = QPushButton(">")
        self.btn_nasledujici.setFixedWidth(40)
        self.btn_nasledujici.setStyleSheet("font-size: 18px;")
        self.btn_nasledujici.clicked.connect(self.nasledujici_den)

        stredni_layout.addWidget(self.btn_predchozi)
        stredni_layout.addWidget(self.kalendar)
        stredni_layout.addWidget(self.btn_nasledujici)
        stredni_widget.setLayout(stredni_layout)

        # Přidat stretch mezi logo a střed, a mezi střed a hodiny
        horni_radek.addStretch()
        horni_radek.addWidget(stredni_widget, alignment=Qt.AlignHCenter)
        horni_radek.addStretch()

        # Hodiny vpravo
        self.clock_label = QLabel()
        self.clock_label.setStyleSheet("font-size: 22px; font-weight: bold; min-width: 80px;")
        horni_radek.addWidget(self.clock_label, alignment=Qt.AlignRight)

        layout.addLayout(horni_radek)

        # Spusť timer pro hodiny
        timer = QTimer(self)
        timer.timeout.connect(self.update_clock)
        timer.start(1000)
        self.update_clock()

        # Záložky pro jednotlivé ordinace
        self.tabulky = {} # mistnost -> QTableWidget
        self.ordinace_layout = QHBoxLayout()  
        
        
        for mistnost in ordinace:
            tabulka = QTableWidget()
            tabulka.setColumnCount(2) # Počet sloupců
            tabulka.setColumnWidth(0, 70) # Čas
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
        
        self.setCentralWidget(central_widget)
    
    
    def show_login_dialog(self):
        dialog = LoginDialog(self)
        if dialog.exec():
            username, role = dialog.get_name_and_role()
            self.logged_in_user = username
            self.logged_in_user_role = role
            self.status_bar.showMessage(f"Přihlášený uživatel: {username}")
            self.login_action.setText("Odhlásit")
            self.login_action.triggered.disconnect()
            self.login_action.triggered.connect(self.logout_user)
            self.update_user_menu()  # <-- Přidat/aktualizovat podmenu

    def logout_user(self):
        self.logged_in_user = None
        self.logged_in_user_role = None
        self.status_bar.showMessage("Nepřihlášen")
        self.login_action.setText("Přihlášení")
        self.login_action.triggered.disconnect()
        self.login_action.triggered.connect(self.show_login_dialog)
        self.update_user_menu()  # <-- Odebrat podmenu
        
    def update_user_menu(self):
        # Odeber staré user_menu, pokud existuje
        if self.user_menu:
            self.menu_bar.removeAction(self.user_menu.menuAction())
            self.user_menu = None

        # Přidej nové podle role
        if self.logged_in_user_role == "admin":
            self.user_menu = QMenu("Nastavení", self)
            self.database_section = QAction("Databáze", self)
            self.plan_surgery_section = QAction("Plánování ordinací", self)
            self.plan_surgery_section.triggered.connect(self.zahaj_planovani_ordinaci)
            self.users_section = QAction("Sekce uživatelů", self)
            self.doctors_section = QAction("Sekce doktoři", self)
            self.surgery_section = QAction("Sekce ordinace", self)
            # Přidejte další akce podle potřeby
            self.menu_bar.addMenu(self.user_menu)
            self.user_menu.addAction(self.database_section)
            self.user_menu.addAction(self.plan_surgery_section)
            self.user_menu.addAction(self.users_section)
            self.user_menu.addAction(self.doctors_section)
            self.user_menu.addAction(self.surgery_section)
        elif self.logged_in_user_role == "supervisor":
            self.user_menu = QMenu("Nastavení", self)
            self.plan_surgery_section = QAction("Plánování ordinací", self)
            self.plan_surgery_section.triggered.connect(self.zahaj_planovani_ordinaci)
            self.users_section = QAction("Sekce uživatelů", self)
            self.doctors_section = QAction("Sekce doktoři", self)
            self.surgery_section = QAction("Sekce ordinace", self)
            # Přidejte další akce podle potřeby
            self.menu_bar.addMenu(self.user_menu)
            self.user_menu.addAction(self.plan_surgery_section)
            self.user_menu.addAction(self.users_section)
            self.user_menu.addAction(self.doctors_section)
            self.user_menu.addAction(self.surgery_section)
        # Pokud není přihlášen, menu se nezobrazí
  
    def zahaj_planovani_ordinaci(self):
        dialog = PlanovaniOrdinaciDialog(self)
        if dialog.exec():
          self.povol_vyber_casu()
  
    def update_clock(self):
        from datetime import datetime
        self.clock_label.setText(datetime.now().strftime("%H:%M:%S"))
        
    def povol_vyber_casu(self):
      def only_first_column_selection():
          for tabulka in self.tabulky.values():
              selected = tabulka.selectedItems()
              for item in selected:
                  if item.column() != 0:
                      item.setSelected(False)
  
      for tabulka in self.tabulky.values():
          tabulka.setSelectionMode(QTableWidget.MultiSelection)
          tabulka.setSelectionBehavior(QTableWidget.SelectRows)
          tabulka.itemSelectionChanged.connect(only_first_column_selection)
          # Nastav žlutou barvu výběru
          tabulka.setStyleSheet("""
              QTableWidget {
                  selection-background-color: yellow;
                  selection-color: black;
              }
          """)
      self.status_bar.showMessage("Vyber časy pouze ve sloupci ČAS a pokračuj tlačítkem Vyber doktora.")
      self.vyber_doktora_btn = QPushButton("Vyber doktora")
      self.dokoncit_planovani_btn = QPushButton("Ukončit plánování")
      self.vyber_doktora_btn.clicked.connect(self.uloz_vybrany_cas_doktora)
      self.dokoncit_planovani_btn.clicked.connect(self.zrus_planovani)
      self.centralWidget().layout().addWidget(self.vyber_doktora_btn)
      self.centralWidget().layout().addWidget(self.dokoncit_planovani_btn)
        
    def zrus_planovani(self):
        # Zrušení plánování a odstranění tlačítka
        self.status_bar.showMessage("Ukončeno plánování ordinací.")
        for tabulka in self.tabulky.values():
            tabulka.setSelectionMode(QTableWidget.NoSelection)
            tabulka.clearSelection()
            self.dokoncit_planovani_btn.deleteLater()
            self.vyber_doktora_btn.deleteLater()    
    
    def uloz_vybrany_cas_doktora(self):
        # Získání vybraných časů a ordinace a uložení do databáze        
        vybrane_casy = []
        mistnost = None
        for m, tabulka in self.tabulky.items():
            for item in tabulka.selectedItems():
                #print(item.text(), item.row(), item.column())
                if item.column() == 0:
                  vybrane_casy.append(item.text())
                  mistnost = m  # Uložení ordinace, pokud je vybrán čas
                    #vybrane_casy.append((m, item.text()))
        dialog = VyberDoktoraDialog(doktori, self)
        if dialog.exec():
            doktor = dialog.get_selected()
            # Uložení do databáze
            datum = self.kalendar.date().toPython()
            vloz_ordinacni_cas(doktor, datum, vybrane_casy[0],vybrane_casy[-1], mistnost)
            self.status_bar.showMessage("Plánování uloženo. Pokračuj v plánování ordinací, nebo jej ukonči.")
        # Vypnutí výběru a odstranění tlačítka
        for tabulka in self.tabulky.values():
            #tabulka.setSelectionMode(QTableWidget.NoSelection)
            tabulka.clearSelection()  # Odznačí všechny vybrané řádky/buňky
        #self.dokoncit_planovani_btn.deleteLater()    
    
    def zpracuj_dvojklik(self, mistnost, row, col):
      tabulka = self.tabulky[mistnost]
      cas_item = tabulka.item(row, 0)
      data_item = tabulka.item(row, 1)
      cas_str = cas_item.text() if cas_item else ""
      data_str = data_item.text() if data_item else ""
  
      if not cas_str:
          return
  
      datum = self.kalendar.date().toPython()
      slot_start = datetime.combine(datum, datetime.strptime(cas_str, "%H:%M").time())
  
      # Zjisti délku slotu stejně jako v nacti_rezervace
      if slot_start.time() >= datetime.strptime("09:00", "%H:%M").time() and slot_start.time() <= datetime.strptime("09:45", "%H:%M").time():
          slot = timedelta(minutes=15)
      elif slot_start.time() >= datetime.strptime("12:00", "%H:%M").time() and slot_start.time() < datetime.strptime("12:30", "%H:%M").time():
          slot = timedelta(minutes=30)
      elif slot_start.time() >= datetime.strptime("12:30", "%H:%M").time() and slot_start.time() < datetime.strptime("12:40", "%H:%M").time():
          slot = timedelta(minutes=10)
      elif slot_start.time() == datetime.strptime("12:40", "%H:%M").time():
          slot = timedelta(minutes=20)
      elif slot_start.time() >= datetime.strptime("16:00", "%H:%M").time() and slot_start.time() <= datetime.strptime("16:30", "%H:%M").time():
          slot = timedelta(minutes=15)
      elif slot_start.time() == datetime.strptime("16:45", "%H:%M").time():
          slot = timedelta(minutes=35)
      elif slot_start.time() >= datetime.strptime("17:20", "%H:%M").time():
          slot = timedelta(minutes=20)
      else:
          slot = timedelta(minutes=20)
  
      slot_end = slot_start + slot
  
      if not data_str.strip():
          # Předvyplň čas a ordinaci
          self.formular = FormularRezervace(self, predvyplneny_cas=f"{datum.strftime('%Y-%m-%d')} {cas_str}", predvyplnena_ordinace=mistnost)
          self.formular.show()
      else:
          rezervace = ziskej_rezervace_dne(datum.strftime("%Y-%m-%d"))
          for r in rezervace:
              # r[8] = mistnost, r[0] = čas rezervace (string)
              rez_cas = datetime.strptime(r[0], "%Y-%m-%d %H:%M")
              if r[8] == mistnost and slot_start <= rez_cas < slot_end:
                  self.formular = FormularRezervace(self, rezervace_data=r)
                  self.formular.show()
                  break    

    def aktualizuj_format_kalendare(self, datum):
        locale = QLocale(QLocale.Czech)
        den = locale.dayName(datum.dayOfWeek(), QLocale.LongFormat)
        self.kalendar.setDisplayFormat(f"'{den} 'd.M.yyyy")

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
          id = r[1] # ID rezervace
          doktor = r[2]
          doktor_color = r[3]
          pacient = r[4]
          majitel = r[5]
          kontakt = r[6]
          druh = r[7]
          mistnost = r[8]
          poznamka = r[9]

          if mistnost in mapovane:
              mapovane[mistnost].append((cas, id, doktor, doktor_color, pacient, majitel, kontakt, druh, poznamka))
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
                  doktor_item = QTableWidgetItem(f"{rez[5]}")  # Majitel
                  font = doktor_item.font()
                  font.setBold(True)
                  doktor_item.setFont(font)
                  # Přidejte tooltip s detaily rezervace
                  tooltip_text = (
                      f"Čas: <b>{cas_str}</b><br>"
                      f"Pacient: <b>{rez[4]}</b><br>"
                      f"Majitel: <b>{rez[5]}</b><br>"
                      f"Kontakt: <b>{rez[6]}</b><br>"
                      f"Druh: <b>{rez[7]}</b><br>"
                      f"Doktor: <b>{rez[2]}</b><br>"
                      f"Poznámka: <b>{rez[8]}</b>"
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
                  if rez[2]:  # Pokud je jméno doktora vyplněné
                      doktor_item.setBackground(QColor(rez[3].strip()))  # Pozadí doktora
                      if vaccination_time == True:
                          tabulka.item(index, 0).setBackground(QColor(vaccination_color))
                      if pause_time == True:
                          tabulka.item(index, 0).setBackground(QColor(pause_color)) 
                  
                  
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
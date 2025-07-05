from PySide6.QtWidgets import (QWidget, QVBoxLayout, QPushButton, QLabel, 
                               QDateEdit, QHBoxLayout, QTableWidget, QApplication,
                               QTableWidgetItem, QMenuBar, QMenu, QMainWindow, QAbstractItemView)
from PySide6.QtCore import QDate, QLocale, QTimer, Qt
from PySide6.QtGui import QColor, QPixmap, QAction, QFont
from nicegui import app
from views.formular_rezervace import FormularRezervace
from models.rezervace import ziskej_rezervace_dne
from datetime import datetime, timedelta
from models.ordinace import get_all_ordinace
from models.doktori import uloz_nebo_uprav_ordinacni_cas, ziskej_rozvrh_doktoru_dne, get_all_doctors_colors, get_doktor_isactive_by_color, uprav_ordinacni_cas
from views.login_dialog import LoginDialog
from controllers.data import table_grey_strip, vaccination_color, pause_color
# from controllers.rezervace_controller import uloz_rezervaci
from models.databaze import get_doktori, set_database_path, inicializuj_databazi
from views.vyber_doktora_dialog import VyberDoktoraDialog
from views.planovani_ordinaci_dialog import PlanovaniOrdinaciDialog
from views.users_dialog import UsersDialog
from views.doctors_dialog import DoctorDialog
from views.ordinace_dialog import OrdinaceDialog
from views.database_setup_dialog import DatabaseSetupDialog
from views.smaz_rezervace_po_xy_dialog import SmazRezervaceDialog
from functools import partial
import os



def get_ordinace_list():
    ordinace = get_all_ordinace()
    # Vytvoř seznam unikátních názvů ordinací
    nazvy = []
    for i in ordinace:
        nazev = f"{i[1]}"
        if nazev not in nazvy:
            nazvy.append(nazev)
    return nazvy

class HlavniOkno(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Veterinární rezervační systém")
        layout = QVBoxLayout()    
        self.logged_in_user = None
        self.logged_in_user_role = None
        
        self.logo_layout = QHBoxLayout()
        self.add_logo()
        
        horni_radek = QHBoxLayout()  # <-- Přesuňte sem vytvoření horni_radek
        self.doktori_layout = QHBoxLayout()
        self.aktualizuj_doktori_layout()
        
        horni_radek.addLayout(self.logo_layout)
        horni_radek.addLayout(self.doktori_layout)
        
        app = QApplication.instance()
        if app:
           # Nastavení delšího timeoutu pro tooltips - BEZ globálního stylingu
           try:
               from PySide6.QtWidgets import QToolTip
               
               # Pouze pokus o nastavení timeoutu - bez CSS
               app.setProperty("toolTipTimeout", 15000)
               
               # Alternativní metody pro timeout
               if hasattr(QToolTip, 'setHideDelay'):
                   QToolTip.setHideDelay(15000)  # 15 sekund
               if hasattr(QToolTip, 'setShowDelay'):
                   QToolTip.setShowDelay(500)    # 0.5 sekundy
                   
           except Exception as e:
               print(f"Tooltip configuration error: {e}")
                
         
        # --- MENU BAR ---
        self.menu_bar = QMenuBar(self)
        self.login_action = QAction("Přihlášení", self)
        self.login_action.triggered.connect(self.show_login_dialog)
        self.menu_bar.addAction(self.login_action)
        
        # Uživatel menu bude přidáváno/odebíráno dynamicky
        self.user_menu = None
        self.database_action = None  # Inicializace pro pozdější použití
        
            
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
                background-color: #f4efeb;
                color: black;
                font-weight: bold;
                font-size: 16px;
                text-decoration: underline;
                letter-spacing: 0.75px;
                text-transform: uppercase;
            }
        """)   
        

        # --- NOVÝ HORIZONTÁLNÍ LAYOUT PRO LOGO, DATUM, HODINY ---

    

        # --- Střední část: tlačítka a kalendář ---
        stredni_widget = QWidget()
        stredni_layout = QHBoxLayout()
        stredni_layout.setContentsMargins(0, 0, 0, 0)
        stredni_layout.setSpacing(10)

        self.btn_predchozi = QPushButton("<")
        self.btn_predchozi.setFixedWidth(40)
        self.btn_predchozi.setStyleSheet("font-size: 20px;")
        self.btn_predchozi.clicked.connect(self.predchozi_den)

        self.kalendar = QDateEdit()
        self.kalendar.setDate(QDate.currentDate())
        self.kalendar.setCalendarPopup(True)
        self.kalendar.setStyleSheet("""
            QDateEdit {
                font-size: 22px;
                min-width: 200px;
                qproperty-alignment: AlignCenter;
                padding: 4px 10px;
            }
        """)
        self.kalendar.dateChanged.connect(self.nacti_rezervace)
        self.kalendar.dateChanged.connect(self.aktualizuj_format_kalendare)
        self.aktualizuj_format_kalendare(self.kalendar.date())

        self.btn_nasledujici = QPushButton(">")
        self.btn_nasledujici.setFixedWidth(40)
        self.btn_nasledujici.setStyleSheet("font-size: 20px;")
        self.btn_nasledujici.clicked.connect(self.nasledujici_den)

        stredni_layout.addWidget(self.btn_predchozi)
        stredni_layout.addWidget(self.kalendar)
        stredni_layout.addWidget(self.btn_nasledujici)
        stredni_widget.setLayout(stredni_layout)

        # Přidat stretch mezi logo a střed, a mezi střed a hodiny
        # horni_radek.addStretch()
        horni_radek.addWidget(stredni_widget, alignment=Qt.AlignHCenter)
        #horni_radek.addStretch()
        
        # Legenda informace vpravo
        def legenda_stylesheet(color):
            return f"""
                background-color: {color};
                color: #222;
                border-radius: 2px;
                min-width: 80px;
                qproperty-alignment: AlignCenter;
                padding: 2px 4px;
                margin-right: 6px;
                font-weight: bold;
            """
        self.legenda_info = QHBoxLayout()
        legenda_vakcinace = QLabel("Vakcinace")
        legenda_vakcinace.setStyleSheet(legenda_stylesheet(vaccination_color))
        
        legenda_pauza = QLabel("Pauza")
        legenda_pauza.setStyleSheet(legenda_stylesheet(pause_color))
        
        self.legenda_info.addWidget(legenda_vakcinace)
        self.legenda_info.addWidget(legenda_pauza)
        horni_radek.addLayout(self.legenda_info)
        self.legenda_info.addStretch()
        
        
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
        
        
        self.aktualizuj_tabulku_ordinaci_layout()
        layout.addLayout(self.ordinace_layout)
        self.setLayout(layout)
        self.nacti_rezervace()
        
        self.setCentralWidget(central_widget)
        
    def aktualizuj_tabulku_ordinaci_layout(self):
        ordinace = get_ordinace_list()   
        # Odstraň všechny widgety z layoutu
        while self.ordinace_layout.count():
            item = self.ordinace_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
    
        # Nyní můžeš bezpečně přidávat nové tabulky
        self.tabulky.clear()
        for mistnost in ordinace:
            tabulka = QTableWidget()
            tabulka.setEditTriggers(QTableWidget.NoEditTriggers)  # Zakázat editaci buněk
            tabulka.setSelectionMode(QAbstractItemView.NoSelection) # Zakázat výběr buněk
            tabulka.setColumnCount(2) # Počet sloupců
            tabulka.setColumnWidth(0, 70) # Čas
            tabulka.horizontalHeader().setStretchLastSection(True)  # Řádek rezervace v maximální šířce
            tabulka.verticalHeader().setVisible(False)

            # Připojení signálu pro dvojklik
            tabulka.cellDoubleClicked.connect(partial(self.zpracuj_dvojklik, mistnost))
            self.ordinace_layout.addWidget(tabulka)
            self.tabulky[mistnost] = tabulka
        self.nacti_rezervace()

    
    
    def add_logo(self):
        # Logo vlevo
        self.logo_label = QLabel()
        logo_path = os.path.join(os.path.dirname(__file__), "../pictures/karakal_logo_grey.png")
        pixmap = QPixmap(logo_path)
        if not pixmap.isNull():
            self.logo_label.setPixmap(pixmap.scaledToHeight(48))
        else:
            self.logo_label.setText("Logo nenalezeno")
        self.logo_layout.addWidget(self.logo_label)
    
    
    def aktualizuj_doktori_layout(self):
      # Odstraň staré widgety ze self.doktori_layout
      while self.doktori_layout.count():
          item = self.doktori_layout.takeAt(0)
          widget = item.widget()
          if widget:
              widget.deleteLater()
      # Přidej nové štítky podle aktuálních dat
      for doktor in get_doktori():
          if doktor[3] == 1:  # Pouze aktivní doktor
              jmeno = f"{doktor[1]}\n{doktor[2]}"
              barva = doktor[5].strip()
              label = QLabel(jmeno)
              label.setStyleSheet(f"""
                  background-color: {barva};
                  color: #222;
                  border-radius: 2px;
                  padding: 2px 4px;
                  margin-right: 6px;
                  font-weight: bold;
              """)
              self.doktori_layout.addWidget(label)
              
              
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
        # Odstranit menu pro plánování, pokud existuje
        # Bezpečně odstranit plan_menu
        if hasattr(self, "plan_menu") and self.plan_menu is not None:
            try:
                self.menu_bar.removeAction(self.plan_menu.menuAction())
            except RuntimeError:
                pass  # plan_menu už může být zničen
            self.plan_menu = None
            
        # Bezpečně odstranit user_menu
        if self.user_menu is not None:
            try:
                self.menu_bar.removeAction(self.user_menu.menuAction())
            except RuntimeError:
                pass
            self.user_menu = None
            
        # Bezpečně odstranit database_action
        if self.database_action is not None:
            try:
                self.menu_bar.removeAction(self.database_action)
            except RuntimeError:
                pass
            self.database_action = None
        
        self.status_bar.showMessage("Nepřihlášen")
        self.login_action.setText("Přihlášení")
        self.login_action.triggered.disconnect()
        self.login_action.triggered.connect(self.show_login_dialog)
        
    def update_user_menu(self):
        """Aktualizuje menu pro uživatele podle jeho role."""
        if self.logged_in_user_role == "user":
            # Pokud je uživatel běžný uživatel, nebudeme přidávat žádné menu
            self.user_menu = None
            return
          
        # Odeber staré user_menu, pokud existuje
        if self.user_menu:
            self.menu_bar.removeAction(self.user_menu.menuAction())
            self.user_menu = None
            
        # Odeber staré database_action, pokud existuje
        if self.database_action:
            self.menu_bar.removeAction(self.database_action)
            self.database_action = None

        # Přidej nové podle role
        
        self.user_menu = QMenu("Nastavení", self)
        
        # Databázové menu jako součást Nastavení
        self.database_section = QAction("Změnit databázi", self)
        self.database_section.triggered.connect(self.change_database)
        
        self.plan_surgery_section = QAction("Plánování ordinací", self)
        self.plan_surgery_section.triggered.connect(self.zahaj_planovani_ordinaci)
        # Přidání sekcí pro administrátora
        self.users_section = QAction("Sekce uživatelů", self)
        self.users_section.triggered.connect(self.sekce_uzivatelu)
        
        # Přidání sekcí pro administrátora
        self.doctors_section = QAction("Sekce doktoři", self)
        self.doctors_section.triggered.connect(self.sekce_doktoru)
        
        self.surgery_section = QAction("Sekce ordinace", self)
        self.surgery_section.triggered.connect(self.sekce_ordinace)
        
        
        self.database_days_deletion_setting = QAction("Nastavení smazání dat", self)
        self.database_days_deletion_setting.triggered.connect(self.nastaveni_smazani_dat)

        # Pokud bylo vytvořeno user_menu, přidej ho do menu_bar a akce
        if self.user_menu:
            self.menu_bar.addMenu(self.user_menu)
            if self.logged_in_user_role == "admin":
                self.user_menu.addAction(self.database_section)  # Pouze pro admina
            self.user_menu.addAction(self.plan_surgery_section)
            self.user_menu.addAction(self.users_section)
            self.user_menu.addAction(self.doctors_section)
            self.user_menu.addAction(self.surgery_section)
            self.user_menu.addAction(self.database_days_deletion_setting)

    def sekce_ordinace(self):
        dialog = OrdinaceDialog(self)
        dialog.exec()

    def sekce_uzivatelu(self):
        dialog = UsersDialog(self, current_user=self.logged_in_user_role)
        dialog.exec()
        
    def sekce_doktoru(self):
        dialog = DoctorDialog(self)
        dialog.exec()
  
    def zahaj_planovani_ordinaci(self):
        self.plan_menu = QMenu("Plánování ordinací", self)
        dialog = PlanovaniOrdinaciDialog(self)
        if dialog.exec():
          self.povol_vyber_casu()
          self.menu_bar.addMenu(self.plan_menu)
          self.menu_bar.removeAction(self.user_menu.menuAction())  # Odstranění Plánování z menu
          for tabulka in self.tabulky.values():  # Odznačí všechny vybrané řádky/buňky
              tabulka.clearSelection()
  
    def update_clock(self):
        self.clock_label.setText(datetime.now().strftime("%H:%M:%S"))
        
    def povol_vyber_casu(self):
      def only_first_column_selection():
          for tabulka in self.tabulky.values():
              #tabulka.setEditTriggers(QTableWidget.AllEditTriggers)  # Zakázat editaci buněk
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
      self.status_bar.showMessage("Vyber časy pouze v prvním sloupci ordinace a pokračuj tlačítkem Plánování ordinací, kde následně Vyber doktora.")
      self.naplanovat_doktora = QAction("Vyber doktora", self) # Tlačítko pro výběr doktora
      self.zrusit_vybrane = QAction("Zrušit vybraný čas doktora", self) # Tlačítko pro zrušení výběru doktora
      self.zrusit_vybrane.triggered.connect(self.zrus_vybrany_cas_doktora) # Přidání akce pro zrušení výběru
      self.ukoncit_planovani_doktora = QAction("Ukončit plánování", self) # Tlačítko pro ukončení plánování
      self.naplanovat_doktora.triggered.connect(self.uloz_vybrany_cas_doktora) # Přidání akce pro uložení vybraných časů a ordinace
      # self.zrusit_vybrane.triggered.connect(self.zrus_vybrany_cas_doktora) # Přidání akce pro uložení vybraných časů a ordinace
      self.ukoncit_planovani_doktora.triggered.connect(self.zrus_planovani) # Zrušení plánování ordinací a odstranění tlačítka
      self.plan_menu.addAction(self.naplanovat_doktora) # Přidání tlačítka pro výběr doktora
      self.plan_menu.addAction(self.zrusit_vybrane) # Přidání tlačítka pro výběr doktora
      self.plan_menu.addAction(self.ukoncit_planovani_doktora) # Přidání tlačítka pro ukončení plánování ordinací

    def zrus_vybrany_cas_doktora(self):
        # Získání vybraných časů a ordinace a uložení do databáze
        all_doctors_colors = [ color[0] for color in get_all_doctors_colors()]
        barvy_puvodnich = []        
        vybrane_casy = []
        mistnost = None
        barva = None
        for m, tabulka in self.tabulky.items():
            for item in tabulka.selectedItems():
                #print(item.text(), item.row(), item.column())
                if item.column() == 0:
                  vybrane_casy.append(item.text())
                  mistnost = m  # Uložení ordinace, pokud je vybrán čas
                  # vybrane_casy.append((m, item.text()))
                  doktor_item = tabulka.item(item.row(), 1)
                  # Získání barvy doktora z buňky    
                  if doktor_item:
                    barva = doktor_item.background().color().name()
                    if barva in all_doctors_colors:
                      if not barva in barvy_puvodnich:
                        barvy_puvodnich.append(barva)
        
        # Uložení do databáze
        datum = self.kalendar.date().toPython()
        # print(f"Barvy doktorů:{barvy_puvodnich}, Datum: {datum}, Čas od: {vybrane_casy[0]}, Čas do: {vybrane_casy[-1]}, Ordinace: {mistnost}")
        # print(vybrane_casy)
        uprav_ordinacni_cas(barvy_puvodnich=barvy_puvodnich, datum=datum, prace_od=vybrane_casy[0], prace_do=vybrane_casy[-1], nazev_ordinace=mistnost)
        self.status_bar.showMessage("Plánování uloženo. Pokračuj v plánování ordinací, nebo jej ukonči.")
        # Vypnutí výběru a odstranění tlačítka
        for tabulka in self.tabulky.values():
            tabulka.clearSelection()  # Odznačí všechny vybrané řádky/buňky
            self.nacti_rezervace()  # Načtení rezervací pro obnovení původního stavu tabulek
        
    def zrus_planovani(self):
        # Zrušení plánování a odstranění tlačítka
        self.status_bar.showMessage("Ukončeno plánování ordinací.")
        self.menu_bar.removeAction(self.plan_menu.menuAction())  # Odstranění Plánování z menu
        self.update_user_menu() # Přidat user menu zpět
        for tabulka in self.tabulky.values():
            tabulka.setSelectionMode(QTableWidget.NoSelection)
            tabulka.clearSelection()
            #self.dokoncit_planovani_btn.deleteLater()
            #self.vyber_doktora_btn.deleteLater() 
            self.nacti_rezervace()  # Načtení rezervací pro obnovení původního stavu tabulek   
    
    def uloz_vybrany_cas_doktora(self):
        # Získání vybraných časů a ordinace a uložení do databáze
        all_doctors_colors = [ color[0] for color in get_all_doctors_colors()]
        match_doctor_colors = []        
        vybrane_casy = []
        mistnost = None
        barva = None
        for m, tabulka in self.tabulky.items():
            for item in tabulka.selectedItems():
                #print(item.text(), item.row(), item.column())
                if item.column() == 0:
                  vybrane_casy.append(item.text())
                  mistnost = m  # Uložení ordinace, pokud je vybrán čas
                  # vybrane_casy.append((m, item.text()))
                  doktor_item = tabulka.item(item.row(), 1)
                  # Získání barvy doktora z buňky    
                  if doktor_item:
                    barva = doktor_item.background().color().name()
                    if barva in all_doctors_colors:
                      if not barva in match_doctor_colors:
                        match_doctor_colors.append(barva)
        dialog = VyberDoktoraDialog(self)
        if dialog.exec():
            new_reservace_doktor = dialog.get_selected()
            # Uložení do databáze
            datum = self.kalendar.date().toPython()
            # print(f"Nový doktor:{new_reservace_doktor}, Starý doktor/doktoři: {match_doctor_colors}, {datum}, {vybrane_casy[0]}, {vybrane_casy[-1]}, {mistnost}")
            # print(vybrane_casy)
            uloz_nebo_uprav_ordinacni_cas(new_reservace_doktor, match_doctor_colors ,datum, vybrane_casy[0],vybrane_casy[-1], mistnost)
            self.status_bar.showMessage("Plánování uloženo. Pokračuj v plánování ordinací, nebo jej ukonči.")
        # Vypnutí výběru a odstranění tlačítka
        for tabulka in self.tabulky.values():
            tabulka.clearSelection()  # Odznačí všechny vybrané řádky/buňky
            self.nacti_rezervace()  # Načtení rezervací pro obnovení původního stavu tabulek
    
    def zpracuj_dvojklik(self, mistnost, row, col):
      if self.logged_in_user_role in ["admin", "supervisor", "user"]:
        tabulka = self.tabulky[mistnost]
        cas_item = tabulka.item(row, 0)
        data_item = tabulka.item(row, 1)
        cas_str = cas_item.text() if cas_item else ""
        data_str = data_item.text() if data_item else ""

        if not cas_str:
            return

        datum = self.kalendar.date().toPython()
        slot_start = datetime.combine(datum, datetime.strptime(cas_str, "%H:%M").time())

        # --- Zjisti jméno a barvu doktora podle rozvrhu ---
        rezervace_doktoru = ziskej_rozvrh_doktoru_dne(datum.strftime("%Y-%m-%d"))
        doktor_jmeno = ""
        for r in rezervace_doktoru:
            # r = (id, jmeno, barva, datum, od, do, ordinace)
            if r[6] == mistnost:
                od = datetime.strptime(r[4], "%H:%M").time()
                do = datetime.strptime(r[5], "%H:%M").time()
                if od <= slot_start.time() <= do:
                    doktor_jmeno = r[1]
                    break
                  
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


        if not data_str.strip():
          # Předvyplň čas, ordinaci a doktora
          self.formular = FormularRezervace(
              self,
              predvyplneny_cas=f"{datum.strftime('%Y-%m-%d')} {cas_str}",
              predvyplnena_ordinace=mistnost,
              predvyplneny_doktor=doktor_jmeno  # <-- přidej tento parametr
          )
          self.formular.show()
        else:
            # ...původní logika pro otevření existující rezervace...
            rezervace = ziskej_rezervace_dne(datum.strftime("%Y-%m-%d"))
            for r in rezervace:
                rez_cas = datetime.strptime(f"{r[0]} {r[10]}", "%Y-%m-%d %H:%M")
                if r[8] == mistnost and slot_start <= rez_cas < slot_start + slot:
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
      rezervace_doktoru = ziskej_rozvrh_doktoru_dne(datum.strftime("%Y-%m-%d"))
      ordinace = get_ordinace_list()
      # print(rezervace_doktoru)
      
      # Debug: Výpis rezervací
      #print(rezervace_doktoru)

      # Vymaž všechny tabulky
      for tabulka in self.tabulky.values():
          tabulka.setRowCount(0)

      # Zmapuj rezervace podle ordinace
      mapovane = {i: [] for i in ordinace}
      for r in rezervace:
          cas = datetime.strptime(f"{r[0]} {r[10]}", "%Y-%m-%d %H:%M")
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
          tabulka.setHorizontalHeaderLabels(["", f"{mistnost}"]) # Set the name of the columne (ordinace)
          
          index = 0
          cas = datetime.combine(datum, datetime.strptime("08:00", "%H:%M").time())
          end = datetime.combine(datum, datetime.strptime("20:00", "%H:%M").time())
          
          
          rozvrh_doktoru_map = {}
          for r in rezervace_doktoru:
              # r = (id, jmeno, barva, datum, od, do, ordinace)
              ordinace_nazev = r[6]
              if ordinace_nazev not in rozvrh_doktoru_map:
                  rozvrh_doktoru_map[ordinace_nazev] = []
              rozvrh_doktoru_map[ordinace_nazev].append(r)    
          
          while cas <= end:
            # Nastav slot podle času
              pause_time = False
              vaccination_time = False  # inicializace na začátku každého cyklu
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
              
              
              # --- ZDE PŘIDAT KONTROLU ROZVRHU DOKTORA ---
              doktor_bg_color = "#ffffff"  # Výchozí barva pozadí
              doktor_jmeno = ""
              if mistnost in rozvrh_doktoru_map:
                  for r in rozvrh_doktoru_map[mistnost]:
                      # r = (id, jmeno, barva, datum, od, do, ordinace)
                      od = datetime.strptime(r[4], "%H:%M").time()
                      do = datetime.strptime(r[5], "%H:%M").time()
                      if od <= cas.time() <= do:
                        if get_doktor_isactive_by_color(r[2]) == 1:
                          doktor_bg_color = r[2].strip()
                          doktor_jmeno = r[1]
                          break
                        
              # Pokud není rezervace, ponech prázdné buňky
              tabulka.setItem(index, 0, QTableWidgetItem(cas_str))
              doktor_item = QTableWidgetItem("")
              
              # Najdi odpovídající rezervaci pro aktuální čas
              rezervace_pro_cas = [
                rez for rez in mapovane[mistnost] if rez[0] >= cas and rez[0] < cas + slot
              ]
        
          
              if doktor_jmeno:
                  doktor_item.setBackground(QColor(doktor_bg_color))
              tabulka.setItem(index, 1, doktor_item)

              # Vlož data do jednotlivých sloupců
              if rezervace_pro_cas:  # Čas
                for rez in rezervace_pro_cas:
                  # tabulka.insertRow(index)
                  tabulka.setItem(index, 0, QTableWidgetItem(cas_str))  # Čas
                  doktor_item = QTableWidgetItem(f"{rez[5]}")  # Majitel
                  font = doktor_item.font()
                  font.setBold(True)
                  doktor_item.setFont(font)
                  doktor_item.setBackground(QColor(doktor_bg_color))
                  tabulka.setItem(index, 1, doktor_item)
                  # Přidejte tooltip s detaily rezervace
                  tooltip_html = f"""
                      <table style="background-color: {doktor_bg_color}; padding: 8px; border-radius: 6px; border: 3px solid #009688; font-family: Arial; font-size: 14px; color: #222; min-width: 250px; margin: 0; border-collapse: collapse;">
                          <tr><td colspan="2" style="text-align: center; font-weight: bold; font-size: 16px; padding: 4px; border-radius: 3px; margin-bottom: 8px;">
                              🩺 {rez[2]}
                          </td></tr>
                          <tr><td>⏰ Čas:</td><td style="font-weight: bold; padding-top:1px">{cas_str}</td></tr>
                          <tr><td>🐕 Pacient:</td><td style="font-weight: bold; padding-top:1px">{rez[4]}</td></tr>
                          <tr><td>👤 Majitel:</td><td style="font-weight: bold; padding-top:1px">{rez[5]}</td></tr>
                          <tr><td>📞 Kontakt:</td><td style="font-weight: bold; padding-top:1px">{rez[6]}</td></tr>
                          <tr><td>🏷️ Druh:</td><td style="font-weight: bold; padding-top:1px">{rez[7]}</td></tr>
                          <tr><td>📝 Poznámka:</td><td style="font-weight: bold; padding-top:1px">{rez[8]}</td></tr>
                      </table>
                      """

                  doktor_item.setToolTip(tooltip_html)

              # Nastavení světle šedého pozadí pro celý řádek
              if index % 2 == 0:  # Sudý řádek
                  for col in range(2):  # Pro všechny sloupce
                    tabulka.item(index, col).setBackground(QColor(table_grey_strip))
                    if vaccination_time == True:  # Pokud buňka existuje
                      tabulka.item(index, 0).setBackground(QColor(vaccination_color))  # Vakcinační pozadí
                    if doktor_bg_color:
                      tabulka.item(index, 1).setBackground(QColor(doktor_bg_color))
                    if pause_time == True:
                      tabulka.item(index, col).setBackground(QColor(pause_color))
                      
                  index += 1
              else:
                  # Pokud není rezervace, ponech prázdné buňky
                  tabulka.setItem(index, 0, QTableWidgetItem(cas_str))

                  # Nastavení světle šedého pozadí pro každý druhý řádek vaccination_color
                  # Sudý řádek
                  for col in range(2):  # Pro druhé sloupce
                    if index % 2 == 0:  # Pro každý sudý řádek
                      if vaccination_time == True:
                       tabulka.item(index, 0).setBackground(QColor(vaccination_color))
                       tabulka.item(index, 1).setBackground(QColor(table_grey_strip))
                       if doktor_bg_color:
                          tabulka.item(index, 1).setBackground(QColor(doktor_bg_color))
                        
                      elif pause_time == True:
                        
                        tabulka.item(index, col).setBackground(QColor(pause_color))
                      else:
                        tabulka.item(index, col).setBackground(QColor(table_grey_strip))
                        if doktor_bg_color:
                          tabulka.item(index, 1).setBackground(QColor(doktor_bg_color))
                          
                    elif pause_time == True:
                      
                      tabulka.item(index, col).setBackground(QColor(pause_color)) # Pokud je pauza
                    elif vaccination_time == True:
                      tabulka.item(index, 0).setBackground(QColor(vaccination_color))
                      
                                            
                  index += 1
                  
              cas += slot
            
      #print("Rezervace načtené z databáze:", rezervace)
    
    def change_database(self):
        """Zobrazí dialog pro změnu databáze."""
        from PySide6.QtWidgets import QMessageBox
        
        reply = QMessageBox.question(
            self,
            "Změna databáze",
            "Opravdu chcete změnit databázi? Všechny neuložené změny budou ztraceny.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            dialog = DatabaseSetupDialog(self)
            result = dialog.exec()
            
            if result == DatabaseSetupDialog.Accepted:
                new_path = dialog.get_database_path()
                set_database_path(new_path)
                
                try:
                    # Pokud byla vybrána nová databáze, inicializuj ji
                    if not os.path.exists(new_path):
                        inicializuj_databazi()
                        QMessageBox.information(
                            self,
                            "Úspěch", 
                            f"Nová databáze byla úspěšně vytvořena: {new_path}"
                        )
                    else:
                        # Existující databáze - zkontroluj a případně aktualizuj strukturu
                        inicializuj_databazi()
                        QMessageBox.information(
                            self,
                            "Úspěch", 
                            f"Databáze byla úspěšně změněna na: {new_path}"
                        )
                    
                    # Restartuj zobrazení
                    self.aktualizuj_tabulku_ordinaci_layout()
                    self.aktualizuj_doktori_layout()
                    
                except Exception as e:
                    QMessageBox.critical(
                        self,
                        "Chyba",
                        f"Nepodařilo se připojit k databázi: {str(e)}"
                    )
      
    def nastaveni_smazani_dat(self):
      """Zobrazí dialog pro nastavení smazání dat."""
      from PySide6.QtWidgets import QMessageBox
      
      dialog = SmazRezervaceDialog(self)
      if dialog.exec():
          days_to_keep = dialog.get_days()
          if days_to_keep is not None:
              days_to_keep = dialog.set_days_to_keep()
              self.nacti_rezervace()
              QMessageBox.information(
                  self,
                  "Úspěch",
                  f"Nastavení smazání dat bylo úspěšně aktualizováno.\nBylo smazáno {days_to_keep['pocet_smazanych']} rezervací starších než {days_to_keep['datum_hranice']}."
              )
import re
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QPushButton, QLabel, 
                               QDateEdit, QHBoxLayout, QTableWidget, QApplication, QMessageBox,
                               QTableWidgetItem, QMenuBar, QMenu, QMainWindow, QAbstractItemView,
                               QSystemTrayIcon, QCheckBox, QInputDialog, QTabWidget, QDialog)
from PySide6.QtGui import QAction
from PySide6.QtCore import QDate, QLocale, QTimer, Qt
from PySide6.QtGui import QColor, QPixmap, QAction, QFont, QIcon, QShortcut, QKeySequence
from views.formular_rezervace import FormularRezervace
from models.rezervace import ziskej_rezervace_dne
from datetime import datetime, timedelta
from models.ordinace import get_all_ordinace
from models.doktori import uloz_nebo_uprav_ordinacni_cas, ziskej_rozvrh_doktoru_dne, get_all_doctors_colors, get_doktor_isactive_by_color, uprav_ordinacni_cas
from views.login_dialog import LoginDialog
from controllers.data import table_grey_strip, vaccination_color, pause_color, anesthesia_color
# from controllers.rezervace_controller import uloz_rezervaci
from models.databaze import get_doktori, set_database_path, inicializuj_databazi
from config import test_database_connection
from views.vyber_doktora_dialog import VyberDoktoraDialog
from views.planovani_ordinaci_dialog import PlanovaniOrdinaciDialog
from views.users_dialog import UsersDialog
from views.doctors_dialog import DoctorDialog
from views.ordinace_dialog import OrdinaceDialog
from views.database_setup_dialog import DatabaseSetupDialog
from views.postgresql_setup_dialog import PostgreSQLSetupDialog
from views.smaz_rezervace_po_xy_dialog import SmazRezervaceDialog
from views.chat_config_dialog import ChatConfigDialog
from views.time_cell_delegate import TimeCellDelegate
from views.patient_status_dialog import PatientStatusDialog
from views.doctor_calendar_dialog import DoctorCalendarDialog
from functools import partial
from controllers.data import basic_style
import os
from models.rezervace import smaz_rezervace_starsi_nez, aktualizuj_stav_rezervace
from models.settings import get_settings
from chat.chat_widget import ChatWidget
import json  # Přidejte tento import

# Smazání rezervací starších než nastavený počet dní
smaz_rezervace_starsi_nez(get_settings("days_to_keep"))


def get_ordinace_list():
    """Optimalizovaná funkce pro získání seznamu názvů ordinací."""
    from models.databaze import get_connection
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute('SELECT DISTINCT nazev FROM Ordinace ORDER BY nazev')
        return [row[0] for row in cur.fetchall()]

class HlavniOkno(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Veterinární rezervační systém")
        # Nastavení ikony aplikace a okna
        self.setup_icons()
        layout = QVBoxLayout()    
        self.logged_in_user = None
        self.logged_in_user_role = None
        
        # Flag pro detekci aktivního plánování ordinačních časů
        self.is_planning_active = False
        
        # Seznam otevřených dialogů pro sledování
        self.open_dialogs = []
        
        # Inicializace pro případné budoucí rozšíření
        # Real-time synchronizace momentálně zakázána kvůli stabilitě
        
        self.logo_layout = QHBoxLayout()
        self.add_logo()
        
        horni_radek = QHBoxLayout()
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
                   QToolTip.setShowDelay(1500)    # 0.5 sekundy
                   
           except Exception as e:
               print(f"Tooltip configuration error: {e}")
                
         
        # --- MENU BAR ---
        import platform
        current_os = platform.system()
        print(f"🖥️ Detekovaný OS: {current_os}")
        
        self.menu_bar = QMenuBar(self)
        
        # macOS specifické nastavení
        if current_os == "Darwin":  # macOS
            print("🍎 Konfiguruji menu pro macOS...")
            # Na macOS se menu automaticky přesouvá do systémového menu baru
            self.menu_bar.setNativeMenuBar(True)
            
            # Pro macOS musíme vytvořit menu trochu jinak
            # Nejprve vytvořme hlavní aplikační akci
            self.login_action = QAction("Přihlášení", self)
            self.login_action.triggered.connect(self.show_login_dialog)
            
            # Vytvoříme menu "ReservationSystem" 
            app_menu = self.menu_bar.addMenu("ReservationSystem")
            app_menu.addAction(self.login_action)
            
            # Přidáme separator a Quit akci pro správné macOS chování
            app_menu.addSeparator()
            quit_action = QAction("Ukončit ReservationSystem", self)
            quit_action.setShortcut("Cmd+Q")
            quit_action.triggered.connect(self.close)
            app_menu.addAction(quit_action)
            
            # Vytvoříme také Edit menu pro konzistenci s macOS
            edit_menu = self.menu_bar.addMenu("Upravit")
            
            print("🍎 macOS menu struktura vytvořena - hledejte 'ReservationSystem' v horní liště")
            
        else:
            print(f"🖥️ Konfiguruji menu pro {current_os}...")
            # Pro ostatní platformy ponecháme menu v okně
            self.menu_bar.setNativeMenuBar(False)
            
            self.login_action = QAction("Přihlášení", self)
            self.login_action.triggered.connect(self.show_login_dialog)
            self.menu_bar.addAction(self.login_action)
        
        print(f"📋 Menu akce 'Přihlášení' přidána")
        
        # Uživatel menu bude přidáváno/odebíráno dynamicky
        self.user_menu = None
        self.database_action = None  # Inicializace pro pozdější použití

        self.menu_bar.setStyleSheet("margin:0,2,0,2")  # Aplikace základního stylu

        self.setMenuBar(self.menu_bar)  # Přidání menu bar do layoutu
        print(f"✅ Menu bar nastaven")
        
        # --- STATUS BAR ---
        self.status_bar = self.statusBar()
        self.status_bar.showMessage("Nepřihlášen")
        self.status_bar.setContentsMargins(2, 0, 2, 0)  # Minimální margins
        
        # Vytvoření widgetu pro checkboxy v status baru - KOMPAKTNÍ
        self.checkboxy_widget = QWidget()
        self.checkboxy_widget.setMaximumHeight(25)  # Omezit výšku status baru
        self.checkboxy_layout = QHBoxLayout(self.checkboxy_widget)
        self.checkboxy_layout.setContentsMargins(2, 0, 2, 0)  # Minimální margins
        self.checkboxy_layout.setSpacing(5)  # Menší spacing
        
        # Přidání checkboxů do status baru napravo
        self.status_bar.addPermanentWidget(self.checkboxy_widget)
        
        # Slovník pro uložení checkboxů
        self.checkboxy = {}
        
        # --- CENTRÁLNÍ WIDGET A LAYOUT ---
        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)
        
        # Styl pro všechny tabulky v tomto okně - MINIMALIZOVÁNO S PODBARVOVÁNÍM A ČITELNÝM PÍSMEM
        self.setStyleSheet("""
            QTableWidget {
                background-color: #fafdff;
                font-size: 12px;
                color: #222;
                gridline-color: #b2d7ef;
                selection-background-color: #cceeff;
                selection-color: #000;
            }
            QTableWidget::item {
                padding: 0px 1px;
                margin: 0px;
                line-height: 0.9;
            }
            QHeaderView::section {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #e6f3ff, stop: 1 #b3d9ff);
                color: #0066cc;
                font-weight: bold;
                font-size: 11px;
                text-decoration: none;
                letter-spacing: 0.5px;
                text-transform: uppercase;
                padding: 2px 4px;
                margin: 0px;
                max-height: 14px;
                min-height: 14px;
                border: 1px solid #0066cc;
                border-radius: 3px;
                text-align: center;
            }
            
            /* Specifické stylování pro první sloupec (čas) */
            QHeaderView::section:first {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #fff2e6, stop: 1 #ffd9b3);
                color: #cc6600;
                font-size: 10px;
            }
            
            /* Efekt při hover */
            QHeaderView::section:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #cce6ff, stop: 1 #99ccff);
            }
        """)   
        

        # --- NOVÝ HORIZONTÁLNÍ LAYOUT PRO LOGO, DATUM, HODINY ---

    

        # --- Střední část: tlačítka a kalendář --- ULTRA KOMPAKTNÍ VERZE
        stredni_widget = QWidget()
        stredni_widget.setMaximumHeight(35)  # Ultra malá výška středního widgetu
        stredni_layout = QHBoxLayout()
        stredni_layout.setContentsMargins(0, 0, 0, 0)
        stredni_layout.setSpacing(5)  # Zmenšit spacing

        self.btn_predchozi = QPushButton("<")
        self.btn_predchozi.setFixedSize(35, 35)  # Ultra malá tlačítka
        self.btn_predchozi.setStyleSheet("font-size: 16px; padding: 0px;")
        self.btn_predchozi.clicked.connect(self.predchozi_den)

        self.kalendar = QDateEdit()
        self.kalendar.setDate(QDate.currentDate())
        self.kalendar.setCalendarPopup(True)
        self.kalendar.setMaximumHeight(40)  # Ultra malá výška kalendáře
        self.kalendar.setStyleSheet("""
            QDateEdit {
                font-size: 16px;
                min-width: 160px;
                font-weight: bold;
                qproperty-alignment: AlignCenter;
                padding: 1px 2px;
            }
        """)
        self.kalendar.dateChanged.connect(self.nacti_rezervace)
        self.kalendar.dateChanged.connect(self.aktualizuj_format_kalendare)
        self.aktualizuj_format_kalendare(self.kalendar.date())

        self.btn_nasledujici = QPushButton(">")
        self.btn_nasledujici.setFixedSize(35, 35)  # Ultra malá tlačítka
        self.btn_nasledujici.setStyleSheet("font-size: 16px; padding: 0px;")
        self.btn_nasledujici.clicked.connect(self.nasledujici_den)

        stredni_layout.addWidget(self.btn_predchozi)
        stredni_layout.addWidget(self.kalendar)
        stredni_layout.addWidget(self.btn_nasledujici)
        stredni_widget.setLayout(stredni_layout)

        # Přidat stretch mezi logo a střed, a mezi střed a hodiny
        # horni_radek.addStretch()
        horni_radek.addWidget(stredni_widget, alignment=Qt.AlignHCenter)
        #horni_radek.addStretch()
        
        # Legenda informace vpravo - EXTRÉMNĚ KOMPAKTNÍ
        def legenda_stylesheet(color):
            return f"""
                background-color: {color};
                color: #222;
                border-radius: 1px;
                qproperty-alignment: AlignCenter;
                padding: 1px 2px;
                margin-right: 2px;
                font-weight: bold;
                font-size: 12px;
            """
        self.legenda_info = QHBoxLayout()
        legenda_vakcinace = QLabel("Vakcinace")
        legenda_vakcinace.setMaximumHeight(30)
        legenda_vakcinace.setStyleSheet(legenda_stylesheet(vaccination_color))
        
        legenda_pauza = QLabel("Pauza")
        legenda_pauza.setMaximumHeight(30)
        legenda_pauza.setStyleSheet(legenda_stylesheet(pause_color))
        
        legenda_anestezie = QLabel("Anestezie")
        legenda_anestezie.setMaximumHeight(30)
        legenda_anestezie.setStyleSheet(legenda_stylesheet(anesthesia_color))
        
        self.legenda_info.addWidget(legenda_vakcinace)
        self.legenda_info.addWidget(legenda_pauza)
        self.legenda_info.addWidget(legenda_anestezie)
        horni_radek.addLayout(self.legenda_info)
        self.legenda_info.addStretch()
        
        
        # Hodiny vpravo - KOMPAKTNÍ verze
        self.clock_label = QLabel()
        self.clock_label.setMaximumHeight(30)
        self.clock_label.setStyleSheet("font-size: 22px; font-weight: bold; min-width: 40px; padding: 0px;")
        horni_radek.addWidget(self.clock_label, alignment=Qt.AlignRight)

        layout.addLayout(horni_radek)

        # Záložky pro jednotlivé ordinace
        self.tabulky = {} # mistnost -> QTableWidget
        
        # Proměnná pro sledování poslední minuty aktualizace zvýraznění
        self.last_highlight_minute = -1
        
        # Spusť timer pro hodiny a aktualizaci času
        timer = QTimer(self)
        timer.timeout.connect(self.update_clock)
        timer.start(1000)
        self.update_clock()
        
        # Vytvoření pevného kontejneru pro ordinace a chat
        self.ordinace_container = QWidget()
        # Nastavíme nejmenší možnou minimální výšku kontejneru pro maximální prostor pro tabulky
        self.ordinace_container.setMinimumHeight(370)
        
        self.ordinace_layout = QHBoxLayout(self.ordinace_container)
        self.ordinace_layout.setContentsMargins(0, 2, 0, 2)  # Minimální margins
        self.ordinace_layout.setSpacing(5)  # Menší spacing mezi sloupci
        
        # Přidáme neviditelný spacer widget pro zachování layoutu
        self.layout_spacer = QWidget()
        self.layout_spacer.setMinimumHeight(150)  # Menší spacer
        self.layout_spacer.setVisible(False)  # Defaultně skrytý
        self.ordinace_layout.addWidget(self.layout_spacer)
        
        # Chat widget - bude inicializován až při prvním použití
        self.chat = None
        self.chat_initialized = False
        
        layout.addWidget(self.ordinace_container)
        
        self.aktualizuj_tabulku_ordinaci_layout()
        self.nacti_rezervace()
        
        # Nastavení auto-refresh pro synchronizaci více instancí
        self.setup_auto_refresh()
        
        self.setCentralWidget(central_widget)
        
        # Nastavení minimální velikosti pro lepší responzivitu
        self.setMinimumSize(950, 420)  # Nejmenší možná minimální velikost pro maximální prostor tabulkám
        
        # Nastavení listenerů pro database změny
        self.setup_database_listeners()
    
    def resizeEvent(self, event):
        """Jednoduchá responzivní úprava bez rozbíjení layoutu"""
        super().resizeEvent(event)
        
        # Pouze pro velmi malé okna upravíme fonty
        if self.width() < 1200:
            # Menší fonty pro úsporu místa
            self.clock_label.setStyleSheet("font-size: 18px; font-weight: bold; min-width: 60px;")
            self.kalendar.setStyleSheet("""
                QDateEdit {
                    font-size: 18px;
                    min-width: 160px;
                    qproperty-alignment: AlignCenter;
                    padding: 3px 6px;
                }
            """)
        else:
            # Původní velikosti pro větší okna
            self.clock_label.setStyleSheet("font-size: 20px; font-weight: bold; min-width: 70px;")
            self.kalendar.setStyleSheet("""
                QDateEdit {
                    font-size: 20px;
                    min-width: 180px;
                    qproperty-alignment: AlignCenter;
                    padding: 4px 8px;
                }
            """)
        
    def aktualizuj_tabulku_ordinaci_layout(self):
        ordinace = get_ordinace_list()   
        
        # Zachováme chat checkbox před mazáním
        chat_checkbox_state = None
        chat_checkbox_ref = None
        if "Chat" in self.checkboxy:
            chat_checkbox_ref = self.checkboxy["Chat"]
            chat_checkbox_state = chat_checkbox_ref.isChecked()
        
        # Zachováme chat widget před mazáním layoutu
        chat_widget_ref = None
        if hasattr(self, 'chat') and self.chat:
            chat_widget_ref = self.chat
            # Dočasně odebereme chat z layoutu
            if self.ordinace_layout.indexOf(self.chat) != -1:
                self.ordinace_layout.removeWidget(self.chat)
        
        # Vymaž staré checkboxy ze status baru (kromě chatu)
        while self.checkboxy_layout.count():
            item = self.checkboxy_layout.takeAt(0)
            widget = item.widget()
            if widget is not None and widget != chat_checkbox_ref:
                widget.deleteLater()
        
        # Odstraň všechny widgety z layoutu (kromě chatu a spaceru)
        while self.ordinace_layout.count():
            item = self.ordinace_layout.takeAt(0)
            widget = item.widget()
            if widget is not None and widget != chat_widget_ref and widget != getattr(self, 'layout_spacer', None):
                widget.deleteLater()
    
        # Nyní můžeš bezpečně přidávat nové tabulky
        self.tabulky.clear()
        # Vyčisti checkboxy, ale zachovej chat
        ordinace_checkboxy = {k: v for k, v in self.checkboxy.items() if k != "Chat"}
        for checkbox in ordinace_checkboxy.values():
            checkbox.deleteLater()
        if chat_checkbox_ref:
            self.checkboxy = {"Chat": chat_checkbox_ref}
        else:
            self.checkboxy.clear()
        
        for mistnost in ordinace:
            # Vytvoření checkboxu pro status bar
            checkbox = QCheckBox(mistnost)
            checkbox.setChecked(True)  # Defaultně zaškrtnuto (tabulka viditelná)
            checkbox.setStyleSheet("""
                QCheckBox {
                    font-weight: bold;
                    font-size: 10px;
                    padding: 1px 2px;
                    background-color: #f0f0f0;
                    border-radius: 2px;
                    margin: 0px;
                }
                QCheckBox::indicator {
                    width: 12px;
                    height: 12px;
                }
            """)
            
            # Připojení checkboxu k funkci pro skrývání/zobrazování
            checkbox.toggled.connect(partial(self.toggle_tabulka_visibility, mistnost))
            
            # Přidání checkboxu do status baru
            self.checkboxy_layout.addWidget(checkbox)
            self.checkboxy[mistnost] = checkbox
            
            # Vytvoříme kontejner pro vlastní hlavičku a tabulku
            table_container = QWidget()
            table_layout = QVBoxLayout(table_container)
            table_layout.setContentsMargins(0, 0, 0, 0)
            table_layout.setSpacing(0)
            
            # Vytvoříme vlastní sloučenou hlavičku
            custom_header = QLabel(f"{mistnost}")
            custom_header.setStyleSheet("""
                QLabel {
                    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                        stop: 0 #e6f3ff, stop: 1 #b3d9ff);
                    color: #0066cc;
                    font-weight: bold;
                    font-size: 11px;
                    letter-spacing: 0.5px;
                    text-transform: uppercase;
                    padding: 2px 4px;
                    border: 1px solid #0066cc;
                    border-radius: 3px;
                    text-align: center;
                    max-height: 14px;
                    min-height: 14px;
                }
            """)
            custom_header.setAlignment(Qt.AlignCenter)
            table_layout.addWidget(custom_header)
            
            # Vytvoříme tabulku bez hlavičky
            tabulka = QTableWidget()
            tabulka.setEditTriggers(QTableWidget.NoEditTriggers)  # Zakázat editaci buněk
            tabulka.setSelectionMode(QAbstractItemView.NoSelection) # Zakázat výběr buněk
            tabulka.setColumnCount(2) # Počet sloupců
            tabulka.setColumnWidth(0, 70) # Čas
            tabulka.horizontalHeader().setStretchLastSection(True)  # Řádek rezervace v maximální šířce
            tabulka.horizontalHeader().setVisible(False)  # Skryjeme původní hlavičku
            tabulka.verticalHeader().setVisible(False)
            
            # Minimalizace margins pro maximální využití prostoru
            tabulka.setContentsMargins(0, 0, 0, 0)

            # Nastavení extrémně malé výšky řádků pro zobrazení všech 38 řádků
            tabulka.verticalHeader().setDefaultSectionSize(2)  # ULTRA malá výška řádků
            
            # Nastavení delegátu pro sloupec s časem (sloupec 0) pro zobrazení kolečka s barvami doktorů
            time_delegate = TimeCellDelegate(tabulka)
            tabulka.setItemDelegateForColumn(0, time_delegate)

            # Připojení signálu pro dvojklik
            tabulka.cellDoubleClicked.connect(partial(self.zpracuj_dvojklik, mistnost))
            
            # Nastavení kontextového menu pro pravé tlačítko
            tabulka.setContextMenuPolicy(Qt.CustomContextMenu)
            tabulka.customContextMenuRequested.connect(partial(self.zobraz_kontextove_menu, mistnost))
            
            # Připojení synchronizace scrollování
            scrollbar = tabulka.verticalScrollBar()
            scrollbar.valueChanged.connect(partial(self.sync_table_scrolling, mistnost))
            
            # Přidáme tabulku do kontejneru s vlastní hlavičkou
            table_layout.addWidget(tabulka)
            
            # Přidáme kontejner do hlavního layoutu místo tabulky
            self.ordinace_layout.addWidget(table_container)
            self.tabulky[mistnost] = tabulka
            
        # Přidání checkboxu pro chat (pouze pokud ještě neexistuje)
        if "Chat" not in self.checkboxy:
            chat_checkbox = QCheckBox("Chat")
            chat_checkbox.setChecked(False)  # Chat defaultně skrytý
            chat_checkbox.setStyleSheet("""
                QCheckBox {
                    font-weight: bold;
                    font-size: 10px;
                    padding: 1px 2px;
                    background-color: #e8f5e8;
                    border-radius: 2px;
                    margin: 0px;
                    color: #2e7d32;
                }
                QCheckBox::indicator {
                    width: 12px;
                    height: 12px;
                }
            """)
            chat_checkbox.toggled.connect(self.toggle_chat_visibility)
            
            # Přidání možnosti konfigurace při dvojkliku na checkbox
            chat_checkbox.mouseDoubleClickEvent = self.chat_checkbox_double_click
            
            self.checkboxy["Chat"] = chat_checkbox
        
        # Přidej chat checkbox zpět do layoutu
        if "Chat" in self.checkboxy:
            self.checkboxy_layout.addWidget(self.checkboxy["Chat"])
        
        # Přidej chat widget zpět do layoutu pokud byl inicializován a měl by být viditelný
        if chat_widget_ref and chat_checkbox_state:
            self.ordinace_layout.addWidget(chat_widget_ref)
            chat_widget_ref.show()
        elif chat_widget_ref:
            # Chat widget existuje ale neměl by být viditelný
            chat_widget_ref.hide()
        
        self.nacti_rezervace()
        
        # Aplikuj optimální výšku řádků po inicializaci s malým zpožděním
        from PySide6.QtCore import QTimer
        QTimer.singleShot(100, self.apply_optimal_row_height)

    def apply_optimal_row_height(self):
        """Aplikuje optimální výšku řádků podle aktuální velikosti okna"""
        # Pro zobrazení všech 38 řádků (8:00-20:00) potřebujeme ULTRA malé řádky
        # Matematika: 38 řádků × výška + hlavičky + margins ≤ dostupného prostoru
        if self.height() < 600:
            row_height = 2  # ULTRA malé pro velmi malé monitory
        elif self.height() < 700:
            row_height = 3  # EXTRÉMNĚ malé
        elif self.height() < 800:
            row_height = 4  # Velmi malé
        else:
            row_height = 5  # Malé i pro velké monitory
            
        # Aplikuj na všechny tabulky
        for tabulka in self.tabulky.values():
            tabulka.verticalHeader().setDefaultSectionSize(row_height)
            # Minimalizuj všechny možné spacing
            tabulka.setContentsMargins(0, 0, 0, 0)
            # Minimalizace grid lines
            tabulka.setShowGrid(True)  # Zachovat mřížku ale minimální
            # Force update tabulky
            tabulka.updateGeometry()

    def toggle_chat_visibility(self, checked):
        """Skryje nebo zobrazí chat podle stavu checkboxu."""
        if checked:
            if not self.chat_initialized:
                # Zobrazí konfigurační dialog při prvním zapnutí
                self.show_chat_config()
            else:
                # Pokud je chat již inicializován, ale není v layoutu, přidej ho
                if self.chat not in [self.ordinace_layout.itemAt(i).widget() 
                                   for i in range(self.ordinace_layout.count()) 
                                   if self.ordinace_layout.itemAt(i).widget()]:
                    self.ordinace_layout.addWidget(self.chat)
                self.chat.show()
        else:
            if self.chat:
                self.chat.hide()
        
        # Aktualizujeme layout spacer
        self.update_layout_spacer()

    def show_chat_config(self):
        """Zobrazí dialog pro konfiguraci chatu"""
        dialog = ChatConfigDialog(self)
        self.register_dialog(dialog)
        if dialog.exec():
            config = dialog.get_config()
            
            # Pokud chat už existuje, zničíme ho před vytvořením nového
            if self.chat_initialized:
                self.destroy_chat()
            
            self.initialize_chat(config)
        else:
            # Pokud uživatel zruší dialog a chat neexistuje, odškrtni checkbox
            if not self.chat_initialized:
                self.checkboxy["Chat"].setChecked(False)
            self.update_layout_spacer()  # Aktualizujeme spacer

    def initialize_chat(self, config):
        """Inicializuje chat widget s danou konfigurací"""
        try:
            # Určení IP pro klienta
            server_ip = config.get("server_ip", "127.0.0.1")
            if server_ip == "0.0.0.0":
                client_ip = "127.0.0.1"
            else:
                client_ip = server_ip
                
            username = config.get("username", "Uživatel")
            server_port = config.get("server_port", 12345)
            
            # Vytvoření chat widgetu
            self.chat = ChatWidget(
                username=username, 
                server_host=client_ip, 
                server_port=server_port
            )
            
            # Nastavení velikosti chatu
            self.chat.setMinimumWidth(300)
            self.chat.setMaximumWidth(450)
            
            # Nastavení size policy pro lepší chování
            from PySide6.QtWidgets import QSizePolicy
            self.chat.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
            
            # Nastavení rámečku pro lepší vizuální oddělení
            self.chat.setStyleSheet("""
                ChatWidget {
                    border: 2px solid #ccc;
                    border-radius: 8px;
                    background-color: #f9f9f9;
                    margin: 2px;
                }
            """)
            
            # Přidání chatu do layoutu
            self.ordinace_layout.addWidget(self.chat)
            
            self.chat_initialized = True
            
            # Aktualizujeme checkbox
            self.checkboxy["Chat"].setChecked(True)
            
        except Exception as e:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.critical(self, "Chyba", f"Nepodařilo se inicializovat chat:\n{str(e)}")
            self.checkboxy["Chat"].setChecked(False)

    def toggle_tabulka_visibility(self, mistnost, checked):
        """Skryje nebo zobrazí tabulku podle stavu checkboxu."""
        if mistnost in self.tabulky:
            tabulka = self.tabulky[mistnost]
            if checked:
                tabulka.show()
            else:
                tabulka.hide()
        
        # Zkontrolujeme, zda je potřeba zobrazit layout spacer
        self.update_layout_spacer()
    
    def update_layout_spacer(self):
        """Aktualizuje viditelnost layout spaceru podle stavu všech widgetů"""
        # Zkontrolujeme, zda spacer stále existuje
        if not hasattr(self, 'layout_spacer') or self.layout_spacer is None:
            return
            
        # Zkontrolujeme, zda je alespoň jedna tabulka nebo chat viditelný
        any_visible = False
        
        # Zkontrolujeme tabulky ordinací
        for mistnost, checkbox in self.checkboxy.items():
            if mistnost != "Chat" and checkbox.isChecked():
                any_visible = True
                break
        
        # Zkontrolujeme chat
        if not any_visible and "Chat" in self.checkboxy and self.checkboxy["Chat"].isChecked():
            any_visible = True
        
        # Pokud nic není viditelné, zobrazíme spacer pro zachování layoutu
        try:
            self.layout_spacer.setVisible(not any_visible)
        except RuntimeError:
            # Widget byl již smazán, ignorujeme
            pass
    
    def add_logo(self):
        # Logo vlevo
        self.logo_label = QLabel()
        
        # Fix pro PyInstaller - správné určení cesty k resources
        import sys
        if getattr(sys, 'frozen', False):
            # Produkční executable - použij _MEIPASS
            base_path = sys._MEIPASS
        else:
            # Development - relativní cesta
            base_path = os.path.dirname(__file__)
        
        # Zkus najít logo v pictures složce - cross-platform cesty
        logo_paths = [
            os.path.join(base_path, "pictures", "karakal_logo_grey.png"),
            os.path.join(base_path, "..", "pictures", "karakal_logo_grey.png"),
            os.path.join(os.path.dirname(__file__), "..", "pictures", "karakal_logo_grey.png"),
            os.path.join(os.path.dirname(os.path.dirname(__file__)), "pictures", "karakal_logo_grey.png")
        ]
        
        pixmap = None
        logo_found = False
        
        for logo_path in logo_paths:
            if os.path.exists(logo_path):
                pixmap = QPixmap(logo_path)
                if not pixmap.isNull():
                    self.logo_label.setPixmap(pixmap.scaledToHeight(30))  # Logo
                    self.logo_label.setMaximumHeight(30)
                    logo_found = True
                    print(f"✅ Logo načteno z: {logo_path}")
                    break
        
        if not logo_found:
            self.logo_label.setText("Logo nenalezeno")
            print(f"❌ Logo nenalezeno. Hledáno v:")
            for path in logo_paths:
                print(f"   - {path} (exists: {os.path.exists(path)})")
        
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
          # Handle both dictionary (PostgreSQL) and tuple (SQLite) formats
          if isinstance(doktor, dict):
              is_active = doktor['isactive']  # PostgreSQL converts to lowercase
              jmeno = doktor['jmeno']
              prijmeni = doktor['prijmeni']
              barva = doktor['color']
          else:
              is_active = doktor[3]
              jmeno = doktor[1]
              prijmeni = doktor[2]
              barva = doktor[5]
              
          if is_active == 1:  # Pouze aktivní doktor
              jmeno_display = f"{jmeno}\n{prijmeni}"
              jmeno_full = f"{jmeno} {prijmeni}"
              barva = barva.strip() if barva else "#CCCCCC"  # Výchozí barva pro NULL
              
              # Vytvoření tlačítka místo labelu
              button = QPushButton(jmeno_display)
              button.setStyleSheet(f"""
                  QPushButton {{
                      background-color: {barva};
                      color: #222;
                      border: 1px solid #999;
                      border-radius: 4px;
                      padding: 4px 6px;
                      margin-right: 6px;
                      font-weight: bold;
                      font-size: 11px;
                      text-align: center;
                  }}
                  QPushButton:hover {{
                      background-color: {barva};
                      border: 2px solid #333;
                  }}
                  QPushButton:pressed {{
                      background-color: {barva};
                      border: 2px solid #000;
                  }}
              """)
              
              # Připojení funkce pro otevření kalendáře
              button.clicked.connect(partial(self.show_doctor_calendar, jmeno_full, barva))
              
              self.doktori_layout.addWidget(button)
    
    def show_doctor_calendar(self, doctor_name, doctor_color):
        """Zobrazí kalendář služeb pro vybraného doktora"""
        dialog = DoctorCalendarDialog(doctor_name, doctor_color, self)
        self.register_dialog(dialog)  # Registruj dialog pro sledování
        dialog.exec()
              
              
    def show_login_dialog(self):
        dialog = LoginDialog(self)
        self.register_dialog(dialog)
        if dialog.exec():
            username, role = dialog.get_name_and_role()
            self.logged_in_user = username
            self.logged_in_user_role = role
            self.status_bar.showMessage(f"Přihlášený uživatel: {username}")
            
            # Aktualizace login akce - musíme správně detekovat platformu
            import platform
            if platform.system() == "Darwin":  # macOS
                # Na macOS máme akce v různých menu, najdeme je a aktualizujeme
                for action in self.menu_bar.actions():
                    if action.menu():
                        for sub_action in action.menu().actions():
                            if sub_action.text() == "Přihlášení":
                                sub_action.setText("Odhlásit")
                                sub_action.triggered.disconnect()
                                sub_action.triggered.connect(self.logout_user)
                print("🍎 macOS menu akce aktualizovány")
            else:
                # Pro ostatní platformy
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
        
        # Aktualizace login akce - musíme správně detekovat platformu
        import platform
        if platform.system() == "Darwin":  # macOS
            # Na macOS máme akce v různých menu, najdeme je a aktualizujeme
            for action in self.menu_bar.actions():
                if action.menu():
                    for sub_action in action.menu().actions():
                        if sub_action.text() == "Odhlásit":
                            sub_action.setText("Přihlášení")
                            sub_action.triggered.disconnect()
                            sub_action.triggered.connect(self.show_login_dialog)
            print("🍎 macOS menu akce pro odhlášení aktualizovány")
        else:
            # Pro ostatní platformy
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

        self.reset_chat_action = QAction("Resetovat chat", self)
        self.reset_chat_action.triggered.connect(self.reset_chat)

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
            self.user_menu.addAction(self.reset_chat_action)

    def sekce_ordinace(self):
        dialog = OrdinaceDialog(self)
        self.register_dialog(dialog)
        dialog.exec()

    def sekce_uzivatelu(self):
        dialog = UsersDialog(self, current_user=self.logged_in_user_role)
        self.register_dialog(dialog)
        dialog.exec()
        
    def sekce_doktoru(self):
        dialog = DoctorDialog(self)
        self.register_dialog(dialog)
        dialog.exec()
  
    def zahaj_planovani_ordinaci(self):
        self.plan_menu = QMenu("Plánování ordinací", self)
        dialog = PlanovaniOrdinaciDialog(self)
        self.register_dialog(dialog)
        if dialog.exec():
          self.is_planning_active = True  # Nastavit flag - pozastavit auto-refresh
          self.povol_vyber_casu()
          self.menu_bar.addMenu(self.plan_menu)
          self.menu_bar.removeAction(self.user_menu.menuAction())  # Odstranění Plánování z menu
          for tabulka in self.tabulky.values():  # Odznačí všechny vybrané řádky/buňky
              tabulka.clearSelection()
  
    def update_clock(self):
        now = datetime.now()
        self.clock_label.setText(now.strftime("%H:%M:%S"))
        
        # Zkontroluj, zda se změnila minuta a aktualizuj zvýraznění času
        current_minute = now.minute
        if current_minute != self.last_highlight_minute:
            self.last_highlight_minute = current_minute
            self.update_current_time_highlight()

        
    def update_current_time_highlight(self):
        """Projde všechny tabulky a aktualizuje zvýraznění aktuálního času"""
        datum = self.kalendar.date().toPython()
        current_time = datetime.now().time()
        # Pro testování můžete použít simulovaný čas:
        # current_time = datetime.strptime("13:10", "%H:%M").time()
        
        for mistnost, tabulka in self.tabulky.items():
            for row in range(tabulka.rowCount()):
                cas_item = tabulka.item(row, 0)
                if cas_item:
                    cas_str = cas_item.text()
                    if cas_str:
                        try:
                            # Parsujeme čas z buňky
                            cas = datetime.combine(datum, datetime.strptime(cas_str, "%H:%M").time())
                            
                            # Určíme délku slotu (stejná logika jako v nacti_rezervace)
                            if cas.time() >= datetime.strptime("09:00", "%H:%M").time() and cas.time() <= datetime.strptime("09:45", "%H:%M").time():
                                slot = timedelta(minutes=15)
                            elif cas.time() >= datetime.strptime("12:00", "%H:%M").time() and cas.time() < datetime.strptime("12:30", "%H:%M").time():
                                slot = timedelta(minutes=30)
                            elif cas.time() >= datetime.strptime("12:30", "%H:%M").time() and cas.time() < datetime.strptime("12:40", "%H:%M").time():
                                slot = timedelta(minutes=10)
                            elif cas.time() == datetime.strptime("12:40", "%H:%M").time():
                                slot = timedelta(minutes=20)
                            elif cas.time() >= datetime.strptime("16:00", "%H:%M").time() and cas.time() <= datetime.strptime("16:30", "%H:%M").time():
                                slot = timedelta(minutes=15)
                            elif cas.time() == datetime.strptime("16:45", "%H:%M").time():
                                slot = timedelta(minutes=35)
                            elif cas.time() >= datetime.strptime("17:20", "%H:%M").time():
                                slot = timedelta(minutes=20)
                            else:
                                slot = timedelta(minutes=20)
                            
                            slot_start_time = cas.time()
                            slot_end_time = (cas + slot).time()
                            
                            # Zkontrolujeme, zda aktuální čas spadá do tohoto slotu
                            if slot_start_time <= current_time < slot_end_time:
                                # Zvýrazníme aktuální čas
                                from PySide6.QtGui import QFont
                                font = QFont()
                                font.setBold(True)
                                font.setPointSize(10)
                                cas_item.setFont(font)
                            else:
                                # Odebereme zvýraznění z ostatních časů
                                from PySide6.QtGui import QFont
                                font = QFont()
                                font.setBold(False)
                                font.setPointSize(10)
                                cas_item.setFont(font)
                                
                        except ValueError:
                            # Pokud se nepodaří parsovat čas, ignorujeme
                            continue
        
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
                  
                  # Získání barev doktorů z UserRole (uložené pro TimeCellDelegate)
                  doctor_colors = item.data(Qt.UserRole)
                  if doctor_colors and isinstance(doctor_colors, list):
                      for barva in doctor_colors:
                          if barva in all_doctors_colors and barva not in barvy_puvodnich:
                              barvy_puvodnich.append(barva)
        
        # Uložení do databáze
        datum = self.kalendar.date().toPython()
        
        # Check if there are selected times before proceeding
        if not vybrane_casy:
            self.status_bar.showMessage("Žádné časy nejsou vybrané.")
            return
            
        if not barvy_puvodnich:
            self.status_bar.showMessage("Žádný doktor není vybrán.")
            return
            
        uprav_ordinacni_cas(barvy_puvodnich=barvy_puvodnich, datum=datum, prace_od=vybrane_casy[0], prace_do=vybrane_casy[-1], nazev_ordinace=mistnost)
        self.status_bar.showMessage("Plánování uloženo. Pokračuj v plánování ordinací, nebo jej ukonči.")
        # Vypnutí výběru a odstranění tlačítka
        for tabulka in self.tabulky.values():
            tabulka.clearSelection()  # Odznačí všechny vybrané řádky/buňky
            self.nacti_rezervace()  # Načtení rezervací pro obnovení původního stavu tabulek
        
    def zrus_planovani(self):
        # Zrušení plánování a odstranění tlačítka
        self.is_planning_active = False  # Obnovit auto-refresh
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
        self.register_dialog(dialog)
        if dialog.exec():
            new_reservace_doktor = dialog.get_selected()
            
            # Uložení do databáze
            datum = self.kalendar.date().toPython()
            
            uloz_nebo_uprav_ordinacni_cas(new_reservace_doktor, match_doctor_colors ,datum, vybrane_casy[0],vybrane_casy[-1], mistnost)
            self.status_bar.showMessage("Plánování uloženo. Pokračuj v plánování ordinací, nebo jej ukonči.")
        # Vypnutí výběru a odstranění tlačítka
        for tabulka in self.tabulky.values():
            tabulka.clearSelection()  # Odznačí všechny vybrané řádky/buňky
            self.nacti_rezervace()  # Načtení rezervací pro obnovení původního stavu tabulek
    
    def zobraz_kontextove_menu(self, mistnost, position):
        """Přímo otevře dialog pro změnu stavu pacienta při kliknutí pravým tlačítkem"""
        if self.logged_in_user_role not in ["admin", "supervisor", "user"]:
            return
            
        tabulka = self.tabulky[mistnost]
        item = tabulka.itemAt(position)
        
        if item is None:
            return
            
        row = item.row()
        col = item.column()
        
        # Zkontroluj, jestli je v buňce rezervace (sloupec 1)
        if col != 1:
            return
            
        data_item = tabulka.item(row, 1)
        data_str = data_item.text() if data_item else ""
        
        # Zkontroluj, jestli je v buňce rezervace (ne prázdná buňka)
        if not data_str.strip():
            return
            
        # Najdi rezervaci v datech
        reservation_data = self.najdi_rezervaci_pro_radek(mistnost, row)
        if reservation_data is None:
            return
            
        # Přímo otevři dialog pro změnu stavu
        self.zmenit_stav_pacienta(reservation_data)
    
    def najdi_rezervaci_pro_radek(self, mistnost, row):
        """Najde rezervaci podle řádku v tabulce"""
        datum = self.kalendar.date().toPython()
        rezervace_dne = ziskej_rezervace_dne(datum.strftime("%Y-%m-%d"))
        
        tabulka = self.tabulky[mistnost]
        cas_item = tabulka.item(row, 0)
        cas_str = cas_item.text() if cas_item else ""
        
        if not cas_str:
            return None
            
        # Převeď čas z buňky na datetime pro porovnání
        cas_slot = datetime.strptime(cas_str, "%H:%M").time()
        
        # Najdi rezervaci, která odpovídá času a ordinaci
        for rez in rezervace_dne:
            if rez[8] == mistnost:  # Správná ordinace
                # rez[10] je cas_od, rez[11] je cas_do
                cas_od = datetime.strptime(rez[10], "%H:%M").time() if isinstance(rez[10], str) else rez[10]
                cas_do = datetime.strptime(rez[11], "%H:%M").time() if isinstance(rez[11], str) else rez[11]
                
                # Zkontroluj, jestli čas slotu spadá do rezervace
                if cas_od <= cas_slot < cas_do or cas_od == cas_slot:
                    return rez
        return None
    
    def zmenit_stav_pacienta(self, reservation_data):
        """Otevře dialog pro změnu stavu pacienta"""
        dialog = PatientStatusDialog(reservation_data, self)
        if dialog.exec() == QDialog.Accepted:
            selected_status = dialog.get_selected_status()
            # Změna: zpracováváme i hodnotu None
            rezervace_id = reservation_data[1]  # ID rezervace
            
            if aktualizuj_stav_rezervace(rezervace_id, selected_status):
                # Force refresh dat - malé zpoždění pro synchronizaci databáze
                QTimer.singleShot(100, self.nacti_rezervace)
                status_text = "nulován" if selected_status is None else selected_status
                # QMessageBox.information(self, "Úspěch", f"Stav pacienta byl změněn na: {status_text}")
            else:
                QMessageBox.warning(self, "Chyba", "Nepodařilo se aktualizovat stav pacienta")

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
          self.register_dialog(self.formular)  # Zaregistruj dialog
          self.center_dialog_on_screen(self.formular)
          self.formular.show()
        else:
            # ...původní logika pro otevření existující rezervace...
            rezervace = ziskej_rezervace_dne(datum.strftime("%Y-%m-%d"))
            for r in rezervace:
                # Handle both datetime object (PostgreSQL) and string (SQLite) formats for r[0]
                if isinstance(r[0], datetime):
                    # PostgreSQL returns datetime objects
                    datum_str = r[0].strftime("%Y-%m-%d")
                else:
                    # SQLite returns strings
                    datum_str = str(r[0])
                    
                rez_cas = datetime.strptime(f"{datum_str} {r[10]}", "%Y-%m-%d %H:%M")
                if r[8] == mistnost and slot_start <= rez_cas < slot_start + slot:
                    self.formular = FormularRezervace(self, rezervace_data=r)
                    self.register_dialog(self.formular)  # Zaregistruj dialog
                    self.center_dialog_on_screen(self.formular)
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
      
      # Vymaž všechny tabulky
      for tabulka in self.tabulky.values():
          tabulka.setRowCount(0)

      # Zmapuj rezervace podle ordinace
      mapovane = {i: [] for i in ordinace}
      for r in rezervace:
          try:
              # Handle both datetime object (PostgreSQL) and string (SQLite) formats for r[0]
              if isinstance(r[0], datetime):
                  # PostgreSQL returns datetime objects
                  datum_str = r[0].strftime("%Y-%m-%d")
              else:
                  # SQLite returns strings
                  datum_str = str(r[0])
                  
              # Combine date and time properly
              cas_od = datetime.strptime(f"{datum_str} {r[10]}", "%Y-%m-%d %H:%M")
              cas_do = datetime.strptime(f"{datum_str} {r[11]}", "%Y-%m-%d %H:%M")
              
              id = r[1]
              doktor = r[2] if r[2] else None  # Může být null
              doktor_color = r[3] if r[3] else None  # Může být null
              pacient = r[4] if r[4] else ""
              majitel = r[5] if r[5] else ""
              kontakt = r[6] if r[6] else ""
              druh = r[7] if r[7] else ""
              mistnost = r[8] if r[8] else ""
              poznamka = r[9] if r[9] else ""
              anestezie = r[12] if r[12] == True else None
              druhy_doktor = f"{r[13]}" if r[13] is not None else None
              barva_druhy_doktor = r[14] if r[14] is not None else None
              stav = r[15] if len(r) > 15 else None  # Stav rezervace
              

              if mistnost and mistnost in mapovane:
                  mapovane[mistnost].append((cas_od, cas_do, id, doktor, doktor_color, pacient, majitel, kontakt, druh, poznamka, anestezie, druhy_doktor, barva_druhy_doktor, stav))
          except (ValueError, IndexError, AttributeError) as e:
              # Pokud je problém s formátem dat rezervace, přeskoč ji
              print(f"Chyba při zpracování rezervace: {e}")
              continue
          
      # Vlož data do tabulek
      for mistnost, tabulka in self.tabulky.items():
          # Tabulka už má vlastní sloučenou hlavičku, nastavíme prázdné labely
          tabulka.setHorizontalHeaderLabels(["", ""])
          
          # Sloučíme dvě buňky hlavičky do jedné
          header = tabulka.horizontalHeader()
          header.setSectionResizeMode(0, header.ResizeMode.Interactive)
          header.setSectionResizeMode(1, header.ResizeMode.Stretch)
          header.resizeSection(1, 1)  # Skryjeme druhou sekci hlavičky

          
          index = 0
          cas = datetime.combine(datum, datetime.strptime("08:00", "%H:%M").time())
          end = datetime.combine(datum, datetime.strptime("20:00", "%H:%M").time())
          
          rozvrh_doktoru_map = {}
          # Bezpečně zpracuj rezervace doktorů - může být prázdné
          if rezervace_doktoru:
              for r in rezervace_doktoru:
                  if r and len(r) > 6:  # Zkontroluj, že záznam má všechny potřebné položky
                      ordinace_nazev = r[6]
                      if ordinace_nazev not in rozvrh_doktoru_map:
                          rozvrh_doktoru_map[ordinace_nazev] = []
                      rozvrh_doktoru_map[ordinace_nazev].append(r)    
          
          while cas <= end:
              pause_time = False
              vaccination_time = False
              
              # Nastav slot podle času
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
              elif cas.time() >= datetime.strptime("16:00", "%H:%M").time() and cas.time() <= datetime.strptime("16:30", "%H:%M").time():
                  slot = timedelta(minutes=15)
                  vaccination_time = True
              elif cas.time() == datetime.strptime("16:45", "%H:%M").time():
                slot = timedelta(minutes=35)
                pause_time = True
              elif cas.time() >= datetime.strptime("17:20", "%H:%M").time():
                  slot = timedelta(minutes=20)
              else:
                  slot = timedelta(minutes=20)
                  
              cas_str = cas.strftime("%H:%M")
              tabulka.insertRow(index)
              
              # Kontrola rozvrhu doktora
              doktor_bg_color = "#ffffff"
              doktor_jmeno = ""
              if mistnost in rozvrh_doktoru_map and rozvrh_doktoru_map[mistnost]:
                  for r in rozvrh_doktoru_map[mistnost]:
                      try:
                          if r and len(r) > 5:  # Zkontroluj, že záznam má všechny potřebné položky
                              od = datetime.strptime(r[4], "%H:%M").time()
                              do = datetime.strptime(r[5], "%H:%M").time()
                              if od <= cas.time() <= do:
                                doktor_active = get_doktor_isactive_by_color(r[2])
                                if doktor_active == 1:
                                  doktor_bg_color = r[2].strip() if r[2] else "#ffffff"
                                  doktor_jmeno = r[1] if r[1] else ""
                                  break
                      except (ValueError, IndexError, AttributeError) as e:
                          # Pokud je problém s formátem dat, pokračuj bez chyby
                          continue
                        
              # Najdi rezervace, které zasahují do aktuálního slotu
              rezervace_pro_cas = []
              for rez in mapovane[mistnost]:
                  cas_od, cas_do = rez[0], rez[1]
                  slot_end = cas + slot
                  
                  # Univerzální logika pro všechny typy rezervací
                  # Rezervace zasahuje do slotu pokud:
                  # začátek rezervace < konec slotu AND konec rezervace >= začátek slotu
                  if cas_od < slot_end and cas_do >= cas:
                      rezervace_pro_cas.append(rez)
              
              # Vytvoř cas_item s barvami doktorů z rezervací i z rozvrhu
              cas_item = QTableWidgetItem(cas_str)
              
              # Zvýrazni aktuální čas tučným písmem ve slotech ordinací
              current_time = datetime.now().time()
              #current_time = datetime.strptime("13:10", "%H:%M").time()
              slot_start_time = cas.time()
              slot_end_time = (cas + slot).time()
              
              # Pokud aktuální čas spadá do tohoto časového slotu, zvýrazni ho
              if slot_start_time <= current_time < slot_end_time:
                  from PySide6.QtGui import QFont
                  font = QFont()
                  font.setBold(True)
                  font.setPointSize(10)  # Trochu větší písmo pro aktuální čas
                  cas_item.setFont(font)
              
              # Shromaždi barvy doktorů z rezervací pro tento čas
              doctor_colors = []
              for rez in rezervace_pro_cas:
                  # Pro každou rezervaci přidej doktory ve správném pořadí
                  # První doktor (index 4 je doktor_color)
                  if rez[4] and rez[4].strip():
                      if rez[4].strip() not in doctor_colors:  # Prevence duplicit
                          doctor_colors.append(rez[4].strip())
                  # Druhý doktor (index 12 je barva_druhy_doktor) - pouze pokud ještě nemáme 2 doktory
                  if len(doctor_colors) < 2 and len(rez) > 12 and rez[12] and rez[12].strip():
                      if rez[12].strip() not in doctor_colors:  # Prevence duplicit
                          doctor_colors.append(rez[12].strip())
                  
                  # Pokud už máme 2 doktory, ukončíme
                  if len(doctor_colors) >= 2:
                      break
              
              # Pokud nejsou rezervace, ale je naplánovaný doktor (rozvrh), přidej jeho barvu
              if not doctor_colors and doktor_bg_color and doktor_bg_color != "#ffffff":
                  doctor_colors.append(doktor_bg_color)
              
              # Ulož barvy do UserRole pro delegate
              cas_item.setData(Qt.UserRole, doctor_colors)
              
              tabulka.setItem(index, 0, cas_item)
              doktor_item = QTableWidgetItem("")
              
              tabulka.setItem(index, 1, doktor_item)

              # Vlož data rezervace
              if rezervace_pro_cas:
                for rez in rezervace_pro_cas:
                  cas_item = QTableWidgetItem(cas_str)
                  
                  # Zvýrazni aktuální čas tučným písmem i v rezervovaných slotech
                  current_time = datetime.now().time()
                  #current_time = datetime.strptime("13:20", "%H:%M").time()
                  slot_start_time = cas.time()
                  slot_end_time = (cas + slot).time()
                  
                  # Pokud aktuální čas spadá do tohoto časového slotu, zvýrazni ho
                  if slot_start_time <= current_time < slot_end_time:
                      from PySide6.QtGui import QFont
                      font = QFont()
                      font.setBold(True)
                      font.setPointSize(10)  # Sjednocená velikost písma
                      cas_item.setFont(font)
                  
                  # Shromaždi barvy doktorů z této konkrétní rezervace
                  doctor_colors = []
                  # První doktor (index 4 je doktor_color) - vždy první pozice
                  if rez[4] and rez[4].strip():
                      doctor_colors.append(rez[4].strip())
                  # Druhý doktor (index 12 je barva_druhy_doktor) - vždy druhá pozice
                  if len(rez) > 12 and rez[12] and rez[12].strip():
                      doctor_colors.append(rez[12].strip())
                  
                  # Ulož barvy do UserRole pro delegate
                  cas_item.setData(Qt.UserRole, doctor_colors)
                  
                  # Nastav správné pozadí pro čas (priorita: vakcinace > pauza > šedý pruh)
                  if vaccination_time:
                      cas_item.setBackground(QColor(vaccination_color))
                  elif pause_time:
                      cas_item.setBackground(QColor(pause_color))
                  elif index % 2 == 0:
                      cas_item.setBackground(QColor(table_grey_strip))
                  
                  tabulka.setItem(index, 0, cas_item)
                  
                  # Zobraz čas od-do pro víceřádkové rezervace
                  cas_od_str = rez[0].strftime("%H:%M")
                  cas_do_str = rez[1].strftime("%H:%M")
                  
                  
                  # Logika pro zobrazení rezervací přes více slotů
                  if rez[0] < rez[1]:  # Rezervace trvá více než jeden slot
                      # Najdi všechny sloty této rezervace v aktuální ordinaci
                      sloty_rezervace = []
                      for r in mapovane[mistnost]:
                          if r[2] == rez[2]:  # Stejné ID rezervace
                              cas_r_od, cas_r_do = r[0], r[1]
                              # Projdi všechny sloty a najdi ty, které patří k této rezervaci
                              temp_cas = datetime.combine(datum, datetime.strptime("08:00", "%H:%M").time())
                              temp_end = datetime.combine(datum, datetime.strptime("20:00", "%H:%M").time())
                              while temp_cas <= temp_end:
                                  # Nastav temp_slot podle času (stejná logika jako výše)
                                  if temp_cas.time() >= datetime.strptime("09:00", "%H:%M").time() and temp_cas.time() <= datetime.strptime("09:45", "%H:%M").time():
                                      temp_slot = timedelta(minutes=15)
                                  elif temp_cas.time() >= datetime.strptime("12:00", "%H:%M").time() and temp_cas.time() < datetime.strptime("12:30", "%H:%M").time():
                                      temp_slot = timedelta(minutes=30)
                                  elif temp_cas.time() >= datetime.strptime("12:30", "%H:%M").time() and temp_cas.time() < datetime.strptime("12:40", "%H:%M").time():
                                      temp_slot = timedelta(minutes=10)
                                  elif temp_cas.time() == datetime.strptime("12:40", "%H:%M").time():
                                      temp_slot = timedelta(minutes=20)
                                  elif temp_cas.time() >= datetime.strptime("16:00", "%H:%M").time() and temp_cas.time() <= datetime.strptime("16:30", "%H:%M").time():
                                      temp_slot = timedelta(minutes=15)
                                  elif temp_cas.time() == datetime.strptime("16:45", "%H:%M").time():
                                      temp_slot = timedelta(minutes=35)
                                  elif temp_cas.time() >= datetime.strptime("17:20", "%H:%M").time():
                                      temp_slot = timedelta(minutes=20)
                                  else:
                                      temp_slot = timedelta(minutes=20)
                                  
                                  temp_slot_end = temp_cas + temp_slot
                                  if cas_r_od < temp_slot_end and cas_r_do >= temp_cas:
                                      sloty_rezervace.append(temp_cas)
                                  temp_cas += temp_slot
                              break
                      
                      # Zjisti pozici aktuálního slotu v seznamu slotů rezervace
                      if cas in sloty_rezervace:
                          pozice = sloty_rezervace.index(cas)
                          if pozice == 0:
                              # První slot - zobraz plné informace
                              display_text = f"{rez[6]}: {rez[8]} - {rez[5]}"
                          elif pozice == len(sloty_rezervace) - 1:
                              # Poslední slot - zobraz plné informace
                              display_text = f"{rez[6]}: {rez[8]} - {rez[5]}"
                          else:
                              # Střední slot - zobraz pouze čárky
                              display_text = "---"
                      else:
                          # Fallback - zobraz plné informace
                          display_text = f"{rez[6]}: {rez[8]} - {rez[5]}"
                  else:
                      # Rezervace v jediném slotu - zobraz plné informace
                      display_text = f"{rez[6]}: {rez[8]} - {rez[5]}"
                  
                  doktor_item = QTableWidgetItem(display_text)
                  font = doktor_item.font()
                  
                  # Nastav styl textu podle stavu rezervace
                  stav = rez[13] if len(rez) > 13 else None  # Stav rezervace (index 13 v novém tuple)
                  
                  if stav == "odbaven":
                      # Škrtlý šedý text pro odbavené pacienty
                      font.setStrikeOut(True)
                      font.setBold(False)  # Ne tučný
                      doktor_item.setForeground(QColor("#888888"))  # Šedý text
                  elif stav == "ceka":
                      # Černý tučný text pro čekající pacienty
                      font.setBold(True)  # Tučný pouze pro "ceka"
                      doktor_item.setForeground(QColor("#000000"))  # Černý text
                  else:
                      # Světle šedý text pro rezervace bez stavu (null)
                      font.setBold(False)  # Ne tučný
                      doktor_item.setForeground(QColor("#888888"))  # Šedý text
                  
                  doktor_item.setFont(font)
                  
                  # Nastav správné pozadí pro rezervaci (priorita: barva doktora > pauza > šedý pruh)
                  if rez[10] == True:  # Pokud je anestezie
                      doktor_item.setBackground(QColor(anesthesia_color)) # Barva pro anestezii
                  elif pause_time:
                      doktor_item.setBackground(QColor(pause_color))
                  elif index % 2 == 0:
                      doktor_item.setBackground(QColor(table_grey_strip))
                  
                  # Přidej vizuální označení pro víceřádkové rezervace
                  if rez[0] < rez[1]:  # Rezervace trvá více než jeden slot
                      # Zjisti pozici slotu v rezervaci (použij už vypočítané hodnoty)
                      if cas in sloty_rezervace:
                          pozice = sloty_rezervace.index(cas)
                          total_sloty = len(sloty_rezervace)
                          
                          # Přidej vizuální označení pro víceřádkové rezervace
                          if total_sloty > 1:
                              # Přidej prefix k textu pro označení pozice
                              current_text = doktor_item.text()
                              if pozice == 0:
                                  # První slot - přidej horní značku
                                  doktor_item.setText(f"┌─ {current_text}")
                              elif pozice == total_sloty - 1:
                                  # Poslední slot - přidej dolní značku
                                  doktor_item.setText(f"└─ {current_text}")
                              else:
                                  # Střední slot - přidej boční značku
                                  if current_text == "---":
                                      doktor_item.setText("│  ---")
                                  else:
                                      doktor_item.setText(f"│  {current_text}")
                  
                  tabulka.setItem(index, 1, doktor_item)
                  
                  # Tooltip s detaily - ošetřit případ kdy doktor může být null
                  doktor_display = rez[3] if rez[3] else "Nepřiřazen"
                  tooltip_html = f"""
                      <table style="background-color:  '#ffffff'; padding: 8px; border-radius: 6px; border: 3px solid #009688; font-family: Arial; font-size: 14px; color: #222; min-width: 250px; margin: 10px; border-collapse: collapse;">
                          <thead>
                          <tr><th colspan="2" style="text-align: center; font-weight: bold; font-size: 16px; padding: 4px; border-radius: 3px; margin-bottom: 8px;">
                            👤 Majitel: {rez[6]}
                          </th></tr>
                          </thead>
                          <tbody>
                          <tr><td colspan="2" style="text-align: center; color: lightgrey">{40*"-"}</td></tr>
                          <tr><td>🐕 Pacient</td><td style="font-weight: bold; padding-top:1px">{rez[5]}</td></tr>
                          <tr><td>🔗 Druh:</td><td style="font-weight: bold; padding-top:1px">{rez[8]}</td></tr>
                          {'<tr><td>🩺 Doktor:</td><td style="font-weight: bold; padding-top:1px">' + doktor_display + '</td></tr>' if doktor_display != "None None" else ""}
                          {'<tr><td style="text-align: center; font-weight: bold; padding:1px 0">💉 Anestezie</td></tr>' if rez[10] == True  else ""}
                          {'<tr><td>🩺🩺 Dokor:</td><td style="font-weight: bold; padding-top:1px">' + rez[11] + '</td></tr>' if rez[11]  else ""}
                          <tr><td>🕰️ Čas:</td><td style="font-weight: bold; padding-top:1px">{cas_od_str} - {cas_do_str}</td></tr>
                          <tr><td>📞 Kontakt:</td><td style="font-weight: bold; padding-top:1px">{rez[7]}</td></tr>
                          <tr><td>📝 Poznámka:</td><td style="font-weight: bold; padding-top:1px">{rez[9]}</td></tr>
                      </tbody>  
                      """
                  doktor_item.setToolTip(tooltip_html)

              # Nastavení pozadí řádků - pouze pokud není rezervace
              if not rezervace_pro_cas:
                  for col in range(2):
                      if tabulka.item(index, col):  # Zkontroluj, že item existuje
                          # Priorita barev: vakcinace (pouze sloupec 0) > pauza > šedý pruh (sudé řádky)
                          if vaccination_time and col == 0:
                              tabulka.item(index, 0).setBackground(QColor(vaccination_color))
                          elif pause_time:
                              tabulka.item(index, col).setBackground(QColor(pause_color))
                          elif index % 2 == 0:
                              tabulka.item(index, col).setBackground(QColor(table_grey_strip))
                      
              index += 1
              cas += slot
      
      # Aplikuj optimální výšku řádků po načtení dat
      self.apply_optimal_row_height()
      
      #print("Rezervace načtené z databáze:", rezervace)
    
    def change_database(self):
        """Zobrazí dialog pro změnu PostgreSQL databáze."""
        
        reply = QMessageBox.question(
            self,
            "Změna databáze",
            "Opravdu chcete změnit konfiguraci PostgreSQL databáze?\n"
            "Aplikace se připojí k nové databázi po uložení nastavení.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            dialog = PostgreSQLSetupDialog(self)
            self.register_dialog(dialog)
            result = dialog.exec()
            
            if result == PostgreSQLSetupDialog.Accepted:
                if dialog.is_connection_successful():
                    QMessageBox.information(
                        self,
                        "Úspěch", 
                        "Konfigurace PostgreSQL databáze byla úspěšně změněna.\n"
                        "Připojení k nové databázi je funkční."
                    )
                    
                    # Aktualizuj zobrazení s novou databází
                    try:
                        self.aktualizuj_tabulku_ordinaci_layout()
                        self.aktualizuj_doktori_layout()
                        self.nacti_rezervace()
                    except Exception as e:
                        QMessageBox.warning(
                            self,
                            "Upozornění",
                            f"Databáze byla změněna, ale došlo k chybě při aktualizaci zobrazení:\n{str(e)}\n\n"
                            "Doporučujeme restartovat aplikaci."
                        )
                else:
                    QMessageBox.warning(
                        self,
                        "Upozornění",
                        "Konfigurace byla uložena, ale test připojení selhal.\n"
                        "Zkontrolujte nastavení a zkuste to znovu."
                    )
      
    def nastaveni_smazani_dat(self):
      """Zobrazí dialog pro nastavení smazání dat."""
      
      dialog = SmazRezervaceDialog(self)
      self.register_dialog(dialog)
      if dialog.exec():
          days_to_keep = dialog.get_days()
          if days_to_keep is not None:
              delete_after = dialog.set_days_to_keep()
              self.nacti_rezervace()
              if delete_after is not None:
                  # Zobraz úspěšnou zprávu
                  QMessageBox.information(
                      self,
                      "Úspěch",
                      f"Nastavení smazání dat bylo úspěšně aktualizováno.\nBylo smazáno {delete_after['pocet_smazanych']} rezervací starších než {delete_after['datum_hranice']}."
                  )
            
    def setup_icons(self):
        """Nastavení ikon pro aplikaci a okno."""
        import sys
        
        # Fix pro PyInstaller - správné určení cesty k resources
        if getattr(sys, 'frozen', False):
            # Produkční executable
            base_path = sys._MEIPASS
        else:
            # Development
            base_path = os.path.dirname(__file__)
        
        # Zkus najít ikonu v různých formátech a umístěních - cross-platform cesty
        icon_paths = [
            # ICO formát (Windows)
            os.path.join(base_path, "pictures", "karakal_logo_grey.ico"),
            os.path.join(base_path, "..", "pictures", "karakal_logo_grey.ico"),
            # PNG formát (fallback)
            os.path.join(base_path, "pictures", "karakal_logo_grey.png"),
            os.path.join(base_path, "..", "pictures", "karakal_logo_grey.png"),
            # Development fallback - cross-platform
            os.path.join(os.path.dirname(__file__), "..", "pictures", "karakal_logo_grey.ico"),
            os.path.join(os.path.dirname(__file__), "..", "pictures", "karakal_logo_grey.png"),
            os.path.join(os.path.dirname(os.path.dirname(__file__)), "pictures", "karakal_logo_grey.ico"),
            os.path.join(os.path.dirname(os.path.dirname(__file__)), "pictures", "karakal_logo_grey.png")
        ]
        
        app_icon = None
        icon_found = False
        
        for icon_path in icon_paths:
            if os.path.exists(icon_path):
                app_icon = QIcon(icon_path)
                if not app_icon.isNull():
                    icon_found = True
                    print(f"✅ Ikona načtena z: {icon_path}")
                    break
        
        if not icon_found:
            print(f"❌ Ikona nenalezena. Hledáno v:")
            for path in icon_paths:
                print(f"   - {path} (exists: {os.path.exists(path)})")
            return
        
        if app_icon and not app_icon.isNull():
            # Nastavení ikony pro okno (levý horní roh)
            self.setWindowIcon(app_icon)
            
            # Nastavení ikony pro celou aplikaci (taskbar, Alt+Tab) - DŮLEŽITÉ POŘADÍ
            app = QApplication.instance()
            if app:
                app.setWindowIcon(app_icon)
                
            # Pro Windows - explicitní nastavení pro všechna okna
            if hasattr(app, 'setWindowIcon'):
                QApplication.setWindowIcon(app_icon)
            
            # System tray ikona...
            if QSystemTrayIcon.isSystemTrayAvailable():
                self.tray_icon = QSystemTrayIcon(app_icon, self)
                
                # Vytvoření kontextového menu pro systémovou lištu
                tray_menu = QMenu()
                
                # Akce pro zobrazení/skrytí okna
                show_action = tray_menu.addAction("Zobrazit")
                show_action.triggered.connect(self.show)
                
                hide_action = tray_menu.addAction("Skrýt")
                hide_action.triggered.connect(self.hide)
                
                tray_menu.addSeparator()
                
                # Akce pro ukončení aplikace
                quit_action = tray_menu.addAction("Ukončit")
                quit_action.triggered.connect(QApplication.instance().quit)
                
                self.tray_icon.setContextMenu(tray_menu)
                
                # Zobrazení ikony v systémové liště
                self.tray_icon.show()
                
                # Tooltip pro ikonu v systémové liště
                self.tray_icon.setToolTip("Veterinární rezervační systém")
                
                # Reakce na kliknutí na ikonu (zobrazí/skryje okno)
                self.tray_icon.activated.connect(self.tray_icon_activated)
                print("✅ System tray ikona nastavena")
            else:
                print("⚠️ Systémová lišta není dostupná")
                self.tray_icon = None
        else:
            print(f"❌ Nepodařilo se načíst žádnou ikonu")
            self.tray_icon = None
            
    def tray_icon_activated(self, reason):
        """Obsluha kliknutí na ikonu v systémové liště."""
        if reason == QSystemTrayIcon.DoubleClick:
            # Dvojklik - zobrazí/skryje okno
            if self.isVisible():
                self.hide()
            else:
                self.show()
                self.raise_()
                self.activateWindow()
        elif reason == QSystemTrayIcon.Trigger:
            # Jednoduché kliknutí - zobrazí okno
            if not self.isVisible():
                self.show()
                self.raise_()
                self.activateWindow()

    def resizeEvent(self, event):
        """Obsluha změny velikosti okna - aplikuj responzivní výšku řádků"""
        super().resizeEvent(event)
        
        # Delay pro lepší výkon - aplikuj změny až po dokončení resizingu
        if hasattr(self, 'resize_timer'):
            self.resize_timer.stop()
        
        from PySide6.QtCore import QTimer
        self.resize_timer = QTimer()
        self.resize_timer.timeout.connect(self.apply_optimal_row_height)
        self.resize_timer.setSingleShot(True)
        self.resize_timer.start(100)  # 100ms delay
        
        print(f"🖥️ Okno změněno na: {self.width()}x{self.height()}px")

    def closeEvent(self, event):
        """Obsluha zavření aplikace"""
        print("🔴 Zavírám hlavní okno a všechna podokna...")
        
        # Zastavení auto-refresh timeru
        if hasattr(self, 'refresh_timer'):
            self.refresh_timer.stop()
        
        # Zastavit database listener
        if hasattr(self, 'db_listener') and self.db_listener:
            try:
                self.db_listener.stop()
                self.db_listener = None
            except Exception as e:
                print(f"Chyba při zastavování database listeneru: {e}")
        
        # Zavři chat pokud je inicializován
        if self.chat_initialized and self.chat:
            try:
                self.chat.close()
            except Exception as e:
                print(f"Chyba při zavírání chatu: {e}")
        
        # Zavři všechna registrovaná podokna (dialogy)
        dialogs_to_close = self.open_dialogs.copy()  # Kopie seznamu
        for dialog in dialogs_to_close:
            try:
                if dialog and hasattr(dialog, 'close'):
                    print(f"🔴 Zavírám registrovaný dialog: {dialog.__class__.__name__}")
                    dialog.close()
                    # Pro QWidget také zajistíme, že se smaže
                    if hasattr(dialog, 'deleteLater'):
                        dialog.deleteLater()
            except Exception as e:
                print(f"Chyba při zavírání dialogu {dialog}: {e}")
        
        # Vyčistíme seznam
        self.open_dialogs.clear()
        
        # Zavři všechna otevřená podokna (dialogy) - agresivní fallback
        try:
            app = QApplication.instance()
            if app:
                print("🔴 Zavírám všechny widgety aplikace...")
                # Zavři všechny top-level widgety kromě hlavního okna
                for widget in app.topLevelWidgets():
                    if widget != self and widget.isVisible():
                        try:
                            print(f"🔴 Zavírám top-level widget: {widget.__class__.__name__}")
                            widget.close()
                            # Zajistíme, že se widget smaže
                            if hasattr(widget, 'deleteLater'):
                                widget.deleteLater()
                        except Exception as e:
                            print(f"Chyba při zavírání widgetu {widget}: {e}")
                
                # Forceuj ukončení aplikace
                print("🔴 Ukončuji aplikaci...")
                app.closeAllWindows()  # Zavře všechna okna
                app.quit()
                
                # Pokud aplikace stále běží, použij exit
                import sys
                sys.exit(0)
                
        except Exception as e:
            print(f"Chyba při zavírání aplikace: {e}")
            # Poslední možnost - tvrdé ukončení
            import sys
            sys.exit(1)
        
        print("✅ Aplikace byla úspěšně ukončena")
        event.accept()

    def register_dialog(self, dialog):
        """Zaregistruje dialog pro sledování a automatické zavření"""
        if dialog not in self.open_dialogs:
            self.open_dialogs.append(dialog)
            # Připojíme signál pro automatické odregistrování při zavření
            # QDialog má finished signál, QWidget má pouze destroyed
            if hasattr(dialog, 'finished'):
                dialog.finished.connect(lambda: self.unregister_dialog(dialog))
            else:
                # Pro QWidget použijeme destroyed signál
                dialog.destroyed.connect(lambda: self.unregister_dialog(dialog))
    
    def unregister_dialog(self, dialog):
        """Odregistruje dialog ze sledování"""
        if dialog in self.open_dialogs:
            self.open_dialogs.remove(dialog)
    
    def center_dialog_on_screen(self, dialog):
        """Vycentruje dialog uprostřed obrazovky"""
        # Získej rozměry obrazovky
        screen = QApplication.primaryScreen()
        screen_geometry = screen.availableGeometry()
        
        # Získej rozměry dialogu
        dialog_size = dialog.sizeHint()
        if dialog_size.isEmpty():
            dialog_size = dialog.size()
        
        # Vypočítej pozici pro centrování
        x = (screen_geometry.width() - dialog_size.width()) // 2
        y = (screen_geometry.height() - dialog_size.height()) // 2
        
        # Nastav pozici dialogu
        dialog.move(x, y)

    def destroy_chat(self):
        """Kompletně zničí chat widget a resetuje stav"""
        if self.chat_initialized and self.chat:
            try:
                # Odebere chat z layoutu
                if self.ordinace_layout.indexOf(self.chat) != -1:
                    self.ordinace_layout.removeWidget(self.chat)
                
                # Zavře a smaže chat widget
                self.chat.close()
                self.chat.deleteLater()
                self.chat = None
                self.chat_initialized = False
                
                # Odškrtne checkbox
                if "Chat" in self.checkboxy:
                    self.checkboxy["Chat"].setChecked(False)
                
                # Aktualizuje layout spacer
                self.update_layout_spacer()
                
            except Exception as e:
                print(f"Chyba při ničení chatu: {e}")

    def reset_chat(self):
        """Resetuje chat - užitečné pro změnu konfigurace"""
        self.destroy_chat()
        # Chat bude znovu inicializován při dalším zapnutí checkboxu

    def chat_checkbox_double_click(self, event):
        """Obsluha dvojkliku na chat checkbox - otevře konfiguraci"""
        self.show_chat_config()
        # Zabrání standardnímu chování checkboxu
        event.accept()

    def setup_auto_refresh(self):
        """Nastaví automatické obnovování dat pro synchronizaci více instancí."""
        # Timer pro automatické obnovení každých 30 sekund
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.auto_refresh_data)
        self.refresh_timer.start(30000)  # 30 sekund
        
        # Klávesová zkratka F5 pro manuální obnovení
        refresh_shortcut = QShortcut(QKeySequence("F5"), self)
        refresh_shortcut.activated.connect(self.manual_refresh_data)
        
        # Klávesová zkratka Ctrl+R pro rychlé manuální obnovení
        refresh_shortcut_ctrl = QShortcut(QKeySequence("Ctrl+R"), self)
        refresh_shortcut_ctrl.activated.connect(self.manual_refresh_data)
        
        print("🔄 Auto-refresh nastaven (30s interval, F5/Ctrl+R pro manuální)")

    def auto_refresh_data(self):
        """Automatické obnovení dat."""
        try:
            # Přeskočit auto-refresh pokud probíhá plánování ordinačních časů
            if self.is_planning_active:
                print("⏸️ Auto-refresh pozastaven - probíhá plánování ordinačních časů")
                return
                
            print("🔄 Auto-refresh dat...")
            self.nacti_rezervace()
            # Pouze při potřebě aktualizovat i ostatní komponenty:
            # self.aktualizuj_doktori_layout()
            # self.aktualizuj_tabulku_ordinaci_layout()
        except Exception as e:
            print(f"⚠️ Chyba při auto-refresh: {e}")

    def manual_refresh_data(self):
        """Manuální obnovení dat (F5 nebo Ctrl+R)."""
        try:
            print("🔄 Manuální refresh dat (F5/Ctrl+R)...")
            self.nacti_rezervace()
            self.aktualizuj_doktori_layout()
            self.aktualizuj_tabulku_ordinaci_layout()
            
            # Zobraz krátké potvrzení
            if hasattr(self, 'status_bar'):
                self.status_bar.showMessage("✅ Data obnovena", 2000)
        except Exception as e:
            print(f"⚠️ Chyba při manuálním refresh: {e}")
            if hasattr(self, 'status_bar'):
                self.status_bar.showMessage(f"❌ Chyba při obnovení: {e}", 5000)

    def setup_database_listeners(self):
        """Nastaví poslouchání database notifikací."""
        try:
            from models.database_listener import DatabaseListener
            
            self.db_listener = DatabaseListener()
            
            # Připoj signály pro různé typy změn
            self.db_listener.reservation_changed.connect(self.on_reservation_changed)
            self.db_listener.doctor_changed.connect(self.on_doctor_changed)
            self.db_listener.ordinace_changed.connect(self.on_ordinace_changed)
            
            # Spusť listener pro všechny typy změn
            self.db_listener.start_listening(['reservation_changes', 'doctor_changes', 'ordinace_changes'])
            
            print("✅ Database listener nastaven pro rezervace, doktory a ordinace")
        except Exception as e:
            print(f"⚠️ Database listener nedostupný: {e}")
            self.db_listener = None

    def on_reservation_changed(self, data):
        """Reakce na změnu rezervace v databázi."""
        try:
            print(f"🔄 Změna rezervace detekována: {data}")
            
            # Aktualizuj rezervace
            self.nacti_rezervace()
            
            # Zobraz notifikaci uživateli
            operation = data.get('operation', 'UPDATE')
            if hasattr(self, 'status_bar'):
                if operation == 'INSERT':
                    self.status_bar.showMessage("📅 Byla přidána nová rezervace", 3000)
                elif operation == 'UPDATE':
                    self.status_bar.showMessage("🔧 Rezervace byla aktualizována", 3000)
                elif operation == 'DELETE':
                    self.status_bar.showMessage("❌ Rezervace byla smazána", 3000)
                    
        except Exception as e:
            print(f"⚠️ Chyba při zpracování změny rezervace: {e}")

    def on_doctor_changed(self, data):
        """Reakce na změnu doktora v databázi."""
        try:
            print(f"🔄 Změna doktora detekována: {data}")
            
            # Aktualizuj layout doktorů
            self.aktualizuj_doktori_layout()
            
            # Aktualizuj rezervace (mohou obsahovat jména doktorů)
            self.nacti_rezervace()
            
            # Zobraz notifikaci uživateli
            operation = data.get('operation', 'UPDATE')
            if hasattr(self, 'status_bar'):
                if operation == 'UPDATE':
                    self.status_bar.showMessage("👨‍⚕️ Informace o doktorovi byly aktualizovány", 3000)
                elif operation == 'DEACTIVATE':
                    self.status_bar.showMessage("⚠️ Doktor byl deaktivován", 3000)
                elif operation == 'DELETE':
                    self.status_bar.showMessage("❌ Doktor byl odstraněn", 3000)
                    
        except Exception as e:
            print(f"⚠️ Chyba při zpracování změny doktora: {e}")

    def on_ordinace_changed(self, data):
        """Reakce na změnu ordinace v databázi."""
        try:
            print(f"🔄 Změna ordinace detekována: {data}")
            
            operation = data.get('operation', 'UPDATE')
            nazev = data.get('data', {}).get('nazev', 'neznámá')
            
            # Aktualizuj layout ordinací
            self.aktualizuj_tabulku_ordinaci_layout()
            
            # Aktualizuj rezervace (mohou obsahovat názvy ordinací)
            self.nacti_rezervace()
            
            # Zobraz notifikaci uživateli
            if hasattr(self, 'status_bar'):
                if operation == 'INSERT':
                    self.status_bar.showMessage(f"🏥 Byla přidána nová ordinace: {nazev}", 3000)
                elif operation == 'UPDATE':
                    self.status_bar.showMessage(f"🔧 Ordinace {nazev} byla aktualizována", 3000)
                elif operation == 'DELETE':
                    self.status_bar.showMessage(f"❌ Ordinace {nazev} byla odstraněna", 3000)
                    
        except Exception as e:
            print(f"⚠️ Chyba při zpracování změny ordinace: {e}")

    def closeEvent(self, event):
        """Obsluha zavření aplikace"""
        # Zastavit database listener
        if hasattr(self, 'db_listener') and self.db_listener:
            try:
                self.db_listener.stop_listening()
                print("✅ Database listener zastaven")
            except Exception as e:
                print(f"⚠️ Chyba při zastavování database listeneru: {e}")
        
        # Zastavit timery
        if hasattr(self, 'refresh_timer') and self.refresh_timer:
            self.refresh_timer.stop()
        
        event.accept()

    def sync_table_scrolling(self, source_mistnost, value):
        """Synchronizuje scrollování všech tabulek s ordinacemi."""
        # Použijeme flag pro zabránění rekurzi místo odpojování signálů
        if hasattr(self, '_syncing_scroll') and self._syncing_scroll:
            return
            
        self._syncing_scroll = True
        
        try:
            for mistnost, tabulka in self.tabulky.items():
                if mistnost != source_mistnost:
                    scrollbar = tabulka.verticalScrollBar()
                    # Nastavíme stejnou pozici scrollbaru bez odpojování signálů
                    scrollbar.setValue(value)
        finally:
            self._syncing_scroll = False
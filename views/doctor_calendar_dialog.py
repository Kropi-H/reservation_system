from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                               QCalendarWidget, QPushButton, QFrame, QSizePolicy)
from PySide6.QtCore import QDate, Qt, QTimer, QRect
from PySide6.QtGui import QTextCharFormat, QColor, QPainter, QFont
from models.doktori import ziskej_rozvrh_doktoru_dne
from datetime import datetime, date
import calendar as cal
import locale

class CustomCalendarWidget(QCalendarWidget):
    """Vlastní kalendář s přepsaným vykreslováním buněk"""
    
    def __init__(self, doctor_name, doctor_color, parent=None):
        super().__init__(parent)
        self.doctor_name = doctor_name
        self.doctor_color = doctor_color
        self.service_days = set()  # Dny se službou
        
    def set_service_days(self, service_days):
        """Nastaví dny se službou"""
        self.service_days = service_days
        self.update()
        
    def paintCell(self, painter, rect, date):
        """Přepsané vykreslování buněk kalendáře"""
        # Konvertujeme QDate na Python date
        py_date = date.toPython()
        from datetime import date as python_date
        today = python_date.today()
        
        # Určíme, jestli má doktor v tento den službu
        has_service = py_date in self.service_days
        is_today = py_date == today
        
        # Nastavíme barvy
        if has_service:
            # Den se službou - barva doktora
            bg_color = QColor(self.doctor_color)
            text_color = QColor("#000000")
        else:
            # Den bez služby - bílé pozadí
            bg_color = QColor("#FFFFFF")
            text_color = QColor("#000000")
        
        # Vykreslíme pozadí
        painter.fillRect(rect, bg_color)
        
        # Nastavíme font
        font = painter.font()
        if is_today:
            font.setBold(True)  # Aktuální den tučně
        else:
            font.setBold(False)
        painter.setFont(font)
        
        # Nastavíme barvu textu
        painter.setPen(text_color)
        
        # Vykreslíme text (číslo dne)
        painter.drawText(rect, Qt.AlignCenter, str(date.day()))
        
        # Pokud je to aktuální den bez služby, přidáme rámeček
        if is_today and not has_service:
            painter.setPen(QColor("#333333"))
            painter.drawRect(rect.adjusted(1, 1, -1, -1))

class DoctorCalendarDialog(QDialog):
    def __init__(self, doctor_name, doctor_color, parent=None):
        super().__init__(parent)
        self.doctor_name = doctor_name
        self.doctor_color = doctor_color.strip() if doctor_color else "#CCCCCC"
        
        self.setWindowTitle(f"Kalendář služeb - {doctor_name}")
        self.setModal(True)
        self.resize(500, 350)
        
        self.setup_ui()
        self.load_doctor_schedule()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Hlavička s informacemi o doktorovi
        header_frame = QFrame()
        header_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {self.doctor_color};
                border-radius: 8px;
                padding: 10px;
                margin-bottom: 10px;
            }}
        """)
        header_layout = QHBoxLayout(header_frame)
        
        # Barevné kolečko
        color_circle = QLabel()
        color_circle.setFixedSize(30, 30)
        color_circle.setStyleSheet(f"""
            QLabel {{
                background-color: {self.doctor_color};
                border: 2px solid #333;
                border-radius: 15px;
            }}
        """)
        
        # Jméno doktora
        name_label = QLabel(self.doctor_name)
        name_label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: bold;
                color: #222;
                padding-left: 10px;
            }
        """)
        
        header_layout.addWidget(color_circle)
        header_layout.addWidget(name_label)
        header_layout.addStretch()
        
        layout.addWidget(header_frame)
        
        # Vlastní navigační lišta
        nav_frame = QFrame()
        nav_frame.setStyleSheet("""
            QFrame {
                background-color: #f0f0f0;
                border: 1px solid #ccc;
                border-radius: 5px;
                padding: 8px;
                margin-bottom: 5px;
            }
        """)
        nav_layout = QHBoxLayout(nav_frame)
        nav_layout.setContentsMargins(10, 5, 10, 5)
        nav_layout.setSpacing(8)
        
        # Tlačítko předchozí měsíc
        self.prev_button = QPushButton("◀")
        self.prev_button.setFixedSize(30, 30)
        self.prev_button.setStyleSheet("""
            QPushButton {
                font-size: 16px;
                font-weight: bold;
                background-color: white;
                border: 1px solid #ccc;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
        """)
        
        # Label pro měsíc a rok
        self.month_year_label = QLabel()
        self.month_year_label.setAlignment(Qt.AlignCenter)
        self.month_year_label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: bold;
                color: #333;
                background-color: white;
                border: 1px solid #ccc;
                border-radius: 3px;
                padding: 4px 12px;
                min-width: 150px;
            }
        """)
        
        # Tlačítko další měsíc
        self.next_button = QPushButton("▶")
        self.next_button.setFixedSize(30, 30)
        self.next_button.setStyleSheet("""
            QPushButton {
                font-size: 16px;
                font-weight: bold;
                background-color: white;
                border: 1px solid #ccc;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
        """)
        
        # Přidání prvků do navigačního layoutu
        nav_layout.addStretch()
        nav_layout.addWidget(self.prev_button)
        nav_layout.addWidget(self.month_year_label)
        nav_layout.addWidget(self.next_button)
        nav_layout.addStretch()
        
        layout.addWidget(nav_frame)
        
        # Kalendář - vlastní implementace
        self.calendar = CustomCalendarWidget(self.doctor_name, self.doctor_color)
        self.calendar.setGridVisible(True)
        self.calendar.setMinimumSize(650, 300)
        
        # Skrytí původní navigační lišty
        self.calendar.setNavigationBarVisible(False)
        
        # Připojení signálů pro vlastní navigaci
        self.prev_button.clicked.connect(self.prev_month)
        self.next_button.clicked.connect(self.next_month)
        
        # Připojení signálu pro kliknutí na den
        self.calendar.clicked.connect(self.on_date_clicked)
        
        # Připojení signálu pro změnu vybraného dne (pro správné formátování aktuálního dne)
        self.calendar.selectionChanged.connect(self.on_selection_changed)
        
        # Tooltip pro kalendář
        self.calendar.setToolTip("Klikněte na den pro přechod na tento datum v hlavním okně")
        
        # Aktualizace labelu měsíce
        self.update_month_label()
        
        # Styly pro kalendář - minimální CSS, který neovlivňuje programové formátování
        self.calendar.setStyleSheet("""
            QCalendarWidget {
                font-size: 12px;
                border: 1px solid #ccc;
                border-radius: 5px;
            }
            QCalendarWidget QTableView {
                gridline-color: #ddd;
            }
        """)
        
        layout.addWidget(self.calendar)
        
        # Tlačítko pro zavření
        button_layout = QHBoxLayout()
        close_button = QPushButton("Zavřít")
        close_button.setStyleSheet("""
            QPushButton {
                background-color: #f0f0f0;
                border: 1px solid #ccc;
                border-radius: 5px;
                padding: 8px 20px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
        """)
        close_button.clicked.connect(self.accept)
        
        button_layout.addStretch()
        button_layout.addWidget(close_button)
        layout.addLayout(button_layout)
        
        # Timer pro pravidelné obnovování formátování (řeší problémy s QCalendarWidget)
        self.format_timer = QTimer()
        self.format_timer.timeout.connect(self.refresh_formatting)
        self.format_timer.start(2000)  # Obnovuj každé 2 sekundy
    
    def load_doctor_schedule(self):
        """Načte rozvrh doktora a označí dny se službou v kalendáři"""
        # Získáme aktuální měsíc a rok z kalendáře
        current_date = self.calendar.selectedDate()
        year = current_date.year()
        month = current_date.month()
        
        # Projdeme všechny dny v aktuálním měsíci a najdeme dny se službou
        days_in_month = cal.monthrange(year, month)[1]
        service_days = set()
        
        for day in range(1, days_in_month + 1):
            check_date = date(year, month, day)
            datum_str = check_date.strftime("%Y-%m-%d")
            
            # Získáme rozvrh pro tento den
            rozvrh = ziskej_rozvrh_doktoru_dne(datum_str)
            
            # Zkontrolujeme, jestli má doktor v tento den službu
            has_service = False
            for r in rozvrh:
                try:
                    # r = (doktor_id, 'Jméno Příjmení', 'Barva', datum, prace_od, prace_do, nazev_ordinace)
                    if len(r) > 1 and str(r[1]).strip() == self.doctor_name.strip():
                        has_service = True
                        break
                except (IndexError, TypeError):
                    # Pokud má záznam neočekávaný formát, přeskočíme ho
                    continue
            
            if has_service:
                service_days.add(check_date)
        
        # Nastavíme dny se službou do vlastního kalendáře
        self.calendar.set_service_days(service_days)
        
        # Připojíme handler pro změnu měsíce/roku
        self.calendar.currentPageChanged.connect(self.on_page_changed)
    
    def on_page_changed(self, year, month):
        """Handler pro změnu stránky kalendáře (měsíc/rok)"""
        # Vyčistíme všechny formáty
        self.calendar.setDateTextFormat(QDate(), QTextCharFormat())
        
        # Znovu načteme rozvrh pro nový měsíc
        self.load_doctor_schedule_for_month(year, month)
    
    def load_doctor_schedule_for_month(self, year, month):
        """Načte rozvrh doktora pro konkrétní měsíc a rok"""
        # Projdeme všechny dny v měsíci a najdeme dny se službou
        days_in_month = cal.monthrange(year, month)[1]
        service_days = set()
        
        for day in range(1, days_in_month + 1):
            check_date = date(year, month, day)
            datum_str = check_date.strftime("%Y-%m-%d")
            
            rozvrh = ziskej_rozvrh_doktoru_dne(datum_str)
            
            has_service = False
            for r in rozvrh:
                try:
                    # r = (doktor_id, 'Jméno Příjmení', 'Barva', datum, prace_od, prace_do, nazev_ordinace)
                    if len(r) > 1 and str(r[1]).strip() == self.doctor_name.strip():
                        has_service = True
                        break
                except (IndexError, TypeError):
                    # Pokud má záznam neočekávaný formát, přeskočíme ho
                    continue
            
            if has_service:
                service_days.add(check_date)
        
        # Nastavíme dny se službou do vlastního kalendáře
        self.calendar.set_service_days(service_days)
    
    def update_month_label(self):
        """Aktualizuje label s názvem měsíce a roku"""
        current_date = self.calendar.selectedDate()
        
        # Česká jména měsíců
        czech_months = [
            "", "Leden", "Únor", "Březen", "Duben", "Květen", "Červen",
            "Červenec", "Srpen", "Září", "Říjen", "Listopad", "Prosinec"
        ]
        
        month_name = czech_months[current_date.month()]
        year = current_date.year()
        
        self.month_year_label.setText(f"{month_name} {year}")
    
    def prev_month(self):
        """Přejde na předchozí měsíc"""
        current_date = self.calendar.selectedDate()
        new_date = current_date.addMonths(-1)
        self.calendar.setSelectedDate(new_date)
        self.update_month_label()
        self.on_page_changed(new_date.year(), new_date.month())
    
    def next_month(self):
        """Přejde na další měsíc"""
        current_date = self.calendar.selectedDate()
        new_date = current_date.addMonths(1)
        self.calendar.setSelectedDate(new_date)
        self.update_month_label()
        self.on_page_changed(new_date.year(), new_date.month())
    
    def refresh_formatting(self):
        """Pravidelně obnovuje formátování kalendáře"""
        current_date = self.calendar.selectedDate()
        self.load_doctor_schedule_for_month(current_date.year(), current_date.month())
        
        # Vynucené překreslení kalendáře
        self.calendar.update()
        self.calendar.repaint()
    
    def on_selection_changed(self):
        """Zpracuje změnu výběru dne - znovu načte formátování"""
        current_date = self.calendar.selectedDate()
        self.load_doctor_schedule_for_month(current_date.year(), current_date.month())
    
    def on_date_clicked(self, date):
        """Zpracuje kliknutí na den v kalendáři"""
        # Převedeme QDate na Python date
        clicked_date = date.toPython()
        
        # Najdeme hlavní okno (parent)
        if self.parent():
            main_window = self.parent()
            
            # Nastavíme datum v hlavním okně
            qdate = QDate.fromString(clicked_date.strftime("%Y-%m-%d"), "yyyy-MM-dd")
            main_window.kalendar.setDate(qdate)
            
            # Aktualizujeme format kalendáře a načteme rezervace
            main_window.aktualizuj_format_kalendare(qdate)
            main_window.nacti_rezervace()
            
            # Zavřeme dialog
            self.accept()
    
    def closeEvent(self, event):
        """Zastaví timer při zavření dialogu"""
        if hasattr(self, 'format_timer'):
            self.format_timer.stop()
        super().closeEvent(event)
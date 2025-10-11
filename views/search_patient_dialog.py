from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLineEdit, 
                               QListWidget, QListWidgetItem, QPushButton, QLabel, 
                               QMessageBox, QSplitter)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from models.databaze import get_connection

class SearchPatientDialog(QDialog):
    # Signal pro předání vybraného data a informací o rezervaci do hlavního okna
    date_selected = Signal(str)  # Posílá datum ve formátu YYYY-MM-DD
    reservation_selected = Signal(str, str, str, str)  # datum, cas_od, cas_do, ordinace
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Vyhledání pacienta")
        self.setModal(True)
        self.resize(600, 500)
        
        # Hlavní layout
        layout = QVBoxLayout(self)
        
        # Vyhledávací pole
        search_layout = QHBoxLayout()
        search_label = QLabel("Vyhledat:")
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Zadejte jméno majitele nebo problém pacienta...")
        self.search_input.textChanged.connect(self.search_patients)
        
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_input)
        layout.addLayout(search_layout)
        
        # Seznam výsledků
        results_label = QLabel("Výsledky vyhledávání:")
        layout.addWidget(results_label)
        
        self.results_list = QListWidget()
        self.results_list.itemDoubleClicked.connect(self.on_item_selected)
        layout.addWidget(self.results_list)
        
        # Tlačítka
        buttons_layout = QHBoxLayout()
        
        self.select_button = QPushButton("Vybrat")
        self.select_button.clicked.connect(self.on_select_clicked)
        self.select_button.setEnabled(False)
        
        cancel_button = QPushButton("Zrušit")
        cancel_button.clicked.connect(self.reject)
        
        buttons_layout.addStretch()
        buttons_layout.addWidget(self.select_button)
        buttons_layout.addWidget(cancel_button)
        layout.addLayout(buttons_layout)
        
        # Připojení selection changed
        self.results_list.itemSelectionChanged.connect(self.on_selection_changed)
        
        # Na začátku nezobrazujeme žádné záznamy
        self.all_patients = []
        self.current_results = []  # Aktuální zobrazené výsledky
        self.display_empty_state()
    
    def search_in_database(self, search_text):
        """Vyhledá pacienty v databázi podle zadaného textu (bez časového omezení)"""
        if not search_text.strip():
            return []
            
        try:
            with get_connection() as conn:
                cur = conn.cursor()
                # Vyhledávání bez časového omezení
                search_pattern = f"%{search_text.lower()}%"
                query = """
                    SELECT DISTINCT 
                        r.termin, 
                        r.cas_od, 
                        r.cas_do,
                        o.nazev,
                        p.majitel_jmeno,
                        p.pacient_problem,
                        p.poznamka,
                        p.majitel_telefon
                    FROM Rezervace r
                    JOIN Pacienti p ON r.pacient_id = p.pacient_id
                    JOIN Ordinace o ON r.ordinace_id = o.ordinace_id
                    WHERE 
                        LOWER(p.majitel_jmeno) LIKE %s OR 
                        LOWER(p.pacient_problem) LIKE %s OR 
                        LOWER(p.poznamka) LIKE %s
                    ORDER BY r.termin DESC, r.cas_od
                """
                cur.execute(query, (search_pattern, search_pattern, search_pattern))
                return cur.fetchall()
                
        except Exception as e:
            QMessageBox.critical(self, "Chyba", f"Nepodařilo se vyhledat pacienty:\n{str(e)}")
            return []
    
    def search_patients(self, search_text):
        """Vyhledá pacienty podle zadaného textu přímo v databázi"""
        if not search_text.strip():
            # Pokud je vyhledávací pole prázdné, zobraz prázdný stav
            self.display_empty_state()
            return
        
        # Pokud má vyhledávací text alespoň 2 znaky, proveď vyhledávání
        if len(search_text.strip()) >= 2:
            results = self.search_in_database(search_text)
            self.display_results(results)
        else:
            # Pro příliš krátký text zobraz informační zprávu
            self.display_short_text_message()
    
    def display_results(self, results):
        """Zobrazí výsledky v seznamu"""
        self.results_list.clear()
        self.current_results = results  # Uložíme aktuální výsledky
        
        for patient in results:
            termin, cas_od, cas_do, ordinace, majitel_jmeno, pacient_problem, poznamka, telefon = patient
            
            # Převedeme termin na string datum (pokud je to datetime objekt)
            if hasattr(termin, 'strftime'):
                datum_str = termin.strftime('%Y-%m-%d')
                datum_display = termin.strftime('%d.%m.%Y')
            else:
                datum_str = str(termin)
                datum_display = datum_str
            
            # Formátování časů (pro případ, že jsou objekty time)
            cas_od_str = cas_od.strftime('%H:%M') if hasattr(cas_od, 'strftime') else str(cas_od)
            cas_do_str = cas_do.strftime('%H:%M') if hasattr(cas_do, 'strftime') else str(cas_do)
            
            # Formátování zobrazení
            display_text = f"{datum_display} {cas_od_str}-{cas_do_str} | {ordinace} | {majitel_jmeno or 'N/A'}"
            if pacient_problem:
                display_text += f" ({pacient_problem})"
            if poznamka:
                display_text += f" - {poznamka}"
            
            item = QListWidgetItem(display_text)
            # Uložíme datum do item data pro pozdější použití (ve formátu YYYY-MM-DD)
            item.setData(Qt.UserRole, datum_str)
            
            self.results_list.addItem(item)
        
        # Zobraz počet výsledků
        count_text = f"Výsledky vyhledávání ({len(results)} nalezeno):"
        results_label = self.layout().itemAt(1).widget()
        if isinstance(results_label, QLabel):
            results_label.setText(count_text)
    
    def display_empty_state(self):
        """Zobrazí prázdný stav při spuštění"""
        self.results_list.clear()
        
        # Zobraz informační zprávu
        info_item = QListWidgetItem("💡 Zadejte jméno majitele, pacienta nebo poznámku pro vyhledání rezervací")
        info_item.setFlags(Qt.ItemFlag.NoItemFlags)  # Nelze vybrat
        from PySide6.QtGui import QFont
        font = QFont()
        font.setItalic(True)
        info_item.setFont(font)
        self.results_list.addItem(info_item)
        
        # Aktualizuj label
        results_label = self.layout().itemAt(1).widget()
        if isinstance(results_label, QLabel):
            results_label.setText("Vyhledávání pacientů:")
    
    def display_short_text_message(self):
        """Zobrazí zprávu o příliš krátkém textu"""
        self.results_list.clear()
        
        # Zobraz informační zprávu
        info_item = QListWidgetItem("⚠️ Zadejte alespoň 2 znaky pro zahájení vyhledávání")
        info_item.setFlags(Qt.ItemFlag.NoItemFlags)  # Nelze vybrat
        from PySide6.QtGui import QFont
        font = QFont()
        font.setItalic(True)
        info_item.setFont(font)
        self.results_list.addItem(info_item)
        
        # Aktualizuj label
        results_label = self.layout().itemAt(1).widget()
        if isinstance(results_label, QLabel):
            results_label.setText("Vyhledávání pacientů:")
    
    def on_selection_changed(self):
        """Aktivuje/deaktivuje tlačítko Vybrat podle výběru"""
        selected_items = self.results_list.selectedItems()
        # Zkontroluj, zda je vybraná položka skutečná rezervace (má UserRole data)
        has_valid_selection = False
        for item in selected_items:
            if item.data(Qt.UserRole) is not None:
                has_valid_selection = True
                break
        
        self.select_button.setEnabled(has_valid_selection)
    
    def on_select_clicked(self):
        """Zpracuje kliknutí na tlačítko Vybrat"""
        selected_items = self.results_list.selectedItems()
        if selected_items:
            self.on_item_selected(selected_items[0])
    
    def on_item_selected(self, item):
        """Zpracuje výběr položky ze seznamu"""
        if item:
            # Získáme datum z item data
            datum = item.data(Qt.UserRole)
            if datum:
                # Získáme další informace o rezervaci z uložených dat
                row = self.results_list.row(item)
                if row < len(self.current_results):
                    rezervace = self.current_results[row]
                    termin, cas_od, cas_do, ordinace = rezervace[0], rezervace[1], rezervace[2], rezervace[3]
                    
                    # Emitujeme signály s datem a detaily rezervace
                    self.date_selected.emit(datum)
                    
                    # Formátujeme časy pro signal
                    cas_od_str = cas_od.strftime('%H:%M') if hasattr(cas_od, 'strftime') else str(cas_od)
                    cas_do_str = cas_do.strftime('%H:%M') if hasattr(cas_do, 'strftime') else str(cas_do)
                    
                    self.reservation_selected.emit(datum, cas_od_str, cas_do_str, ordinace)
                
                self.accept()
            else:
                # Ignoruj informační položky (nemají UserRole data)
                return
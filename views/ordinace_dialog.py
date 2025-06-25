from PySide6.QtWidgets import QDialog, QVBoxLayout, QPushButton, QHBoxLayout, QMessageBox
from PySide6.QtWidgets import QWidget, QLabel, QPushButton, QHBoxLayout, QVBoxLayout, QScrollArea
from views.add_ordinace_dialog import AddOrdinaceDialog
from views.edit_ordinace_dialog import EditOrdinaceDialog
from models.ordinace import get_all_ordinace, add_ordinace, remove_ordinace, update_ordinace_db
from models.rezervace import remove_all_older_rezervations_for_ordinaci
from functools import partial
from models.doktori import remove_all_ordinacni_cas
from models.rezervace import rezervace_pro_ordinaci
from controllers.data import basic_button_color, basic_button_style, q_header_view_style
from datetime import datetime

class OrdinaceDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Správa ordinací")
        self.resize(400, 350)
        self.center_to_parent()
        self.parent_window = parent

        self.layout = QVBoxLayout(self)

        self.button_layout = QHBoxLayout()
        self.add_ordinace_button = QPushButton("Přidat ordinaci", self)
        self.add_ordinace_button.setObjectName("add_ordinace_button")
        self.add_ordinace_button.setStyleSheet(f"background-color: {basic_button_color['add_button_color']};")
        self.add_ordinace_button.clicked.connect(self.add_ordinace)
        self.button_layout.addWidget(self.add_ordinace_button)
        self.layout.addLayout(self.button_layout)

        self.scroll = None  # <-- přidáno
        self.load_ordinace()

        # Styl pro všechny tabulky v tomto okně
        self.setStyleSheet(f"""
            QHeaderView::section {{
                {q_header_view_style}
            }}
            QPushButton#remove_ordinace, 
            QPushButton#update_ordinace,
            QPushButton#change_password,
            QPushButton#add_ordinace_button {{
                {basic_button_style}
            }}
        """)  
 
        
    def center_to_parent(self):
        pass
        if self.parent():
            parent_geom = self.parent().geometry()
            self_geom = self.geometry()
            x = parent_geom.x() + (parent_geom.width() - self_geom.width()) // 2
            y = parent_geom.y() + (parent_geom.height() - self_geom.height()) // 2
            self.move(x, y)


    def load_ordinace(self):
        # Odstraňte starý scroll area, pokud existuje
        if self.scroll is not None:
            self.layout.removeWidget(self.scroll)
            self.scroll.deleteLater()
            self.scroll = None
            
        self.ordinace_widget = QWidget()
        vbox = QVBoxLayout(self.ordinace_widget)
        ordinace = get_all_ordinace()
        for ord in ordinace:
            hbox = QHBoxLayout()
            label = QLabel(f"{ord[1]}")
            label.setStyleSheet("font-weight: bold; font-size: 14px;")
            hbox.addWidget(label)                        

            remove_button = QPushButton("Odebrat")
            remove_button.setObjectName("remove_ordinace")
            remove_button.setStyleSheet(f"background-color: {basic_button_color['remove_button_color']};")
            remove_button.clicked.connect(partial(self.remove_ordinace, ord[0], ord[1]))
            update_button = QPushButton("Upravit")
            update_button.setObjectName("update_ordinace")
            update_button.setStyleSheet(f"background-color: {basic_button_color['update_button_color']};")
            update_button.clicked.connect(partial(self.update_ordinace, ord[0]))

            hbox.addWidget(remove_button)
            hbox.addWidget(update_button)
            vbox.addLayout(hbox)
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setWidget(self.ordinace_widget)
        self.layout.addWidget(self.scroll)

    def add_ordinace(self):
        dialog = AddOrdinaceDialog(self)
        if dialog.exec() == QDialog.Accepted:
            try:
                data = dialog.get_data()
                add_ordinace(data)
                self.load_ordinace()
                if self.parent_window and hasattr(self.parent_window, "aktualizuj_tabulku_ordinaci_layout"):
                      self.parent_window.aktualizuj_tabulku_ordinaci_layout()
                      self.parent_window.nacti_rezervace()
                if self.parent_window:
                    self.parent_window.status_bar.showMessage(f"Ordinace {data['nazev']} byl přidán.")
            except ValueError as ve:
                if self.parent_window:
                    self.parent_window.status_bar.showMessage(str(ve))
            except Exception as e:
                if self.parent_window:
                  self.parent_window.status_bar.showMessage(f"Chyba při přidávání ordinace: {e}")

    def ma_budouci_rezervaci(self, rezervace):
        for _, datum, cas, _ in rezervace:
            if datetime.strptime(f"{datum} {cas}", "%Y-%m-%d %H:%M") > datetime.now():
                return True
        return False
      
    def remove_ordinace(self, ordinace_id, nazev):
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Odebrat ordinaci")
        msg_box.setText(f"Opravdu chcete odebrat ordinaci {nazev}?")
        ano_button = msg_box.addButton("Ano", QMessageBox.YesRole)
        msg_box.addButton("Ne", QMessageBox.NoRole)
        msg_box.exec_()
        if msg_box.clickedButton() == ano_button:
            try:
              # Prohledat databazi, zda pro ordinaci neexistují rezervace
                try:
                    rezervations_for_surgery = rezervace_pro_ordinaci(ordinace_id)
                except Exception as e:
                    QMessageBox.critical(self, "Chyba", f"Chyba při prohledávání rezervací: {e}")
                    return

                if self.ma_budouci_rezervaci(rezervations_for_surgery):
                    QMessageBox.warning(self, "Chyba", f"Ordinace {nazev} má existující rezervace a nemůže být odstraněna.")
                    return
                try:
                    remove_all_older_rezervations_for_ordinaci(ordinace_id) # Odstraní všechny rezervace pro tuto ordinaci
                    remove_all_ordinacni_cas(ordinace_id) # Odstraní všechny ordinace, které jsou spojeny s touto ordinací
                    remove_ordinace(ordinace_id, nazev) # Odstraní ordinaci z databáze
                except Exception as e:
                    QMessageBox.critical(self, "Chyba", f"Chyba při odstraňování ordinace: {e}")
                    return
                self.load_ordinace()
                if self.parent_window:
                    self.parent_window.status_bar.showMessage(f"Ordinace {nazev} byla odebrána.")
                    if self.parent_window and hasattr(self.parent_window, "aktualizuj_tabulku_ordinaci_layout"):
                      self.parent_window.aktualizuj_tabulku_ordinaci_layout()
                      self.parent_window.nacti_rezervace()
            except Exception as e:
                QMessageBox.critical(self, "Chyba", f"Chyba při odstraňování ordinace: {e}")

    def update_ordinace(self, ordinace_id):
        # Najděte aktuální roli ordinace
        all_ordinace = get_all_ordinace()
        ordinace = next((u for u in all_ordinace if u[0] == ordinace_id), None)
        if not ordinace:
            if self.parent_window:
                self.parent_window.status_bar.showMessage("Ordinace nenalezena.")
            return
        ordinace_id = ordinace[0]
        dialog = EditOrdinaceDialog(ordinace_id)
        if dialog.exec() == QDialog.Accepted:
            data = dialog.get_data()
            try:
                update_ordinace_db(ordinace_id, data)
                self.load_ordinace()
                if self.parent_window and hasattr(self.parent_window, "aktualizuj_ordinace_layout"):
                      self.parent_window.aktualizuj_ordinace_layout()
                      self.parent_window.nacti_rezervace()
                if self.parent_window and hasattr(self.parent_window, "aktualizuj_tabulku_ordinaci_layout"):
                      self.parent_window.aktualizuj_tabulku_ordinaci_layout()
                      self.parent_window.nacti_rezervace()
                if self.parent_window:
                    self.parent_window.status_bar.showMessage(f"Ordinace {data['nazev']} upravena.")
            except Exception as e:
                if self.parent_window:
                    self.parent_window.status_bar.showMessage(f"Chyba při úpravě ordinace: {e}")
    
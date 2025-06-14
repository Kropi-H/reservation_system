from PySide6.QtWidgets import QDialog, QVBoxLayout, QPushButton, QHBoxLayout, QMessageBox, QFrame
from PySide6.QtWidgets import QWidget, QLabel, QPushButton, QHBoxLayout, QVBoxLayout, QScrollArea
from PySide6.QtCore import Qt
from views.add_ordinace_dialog import AddOrdinaceDialog
from views.edit_ordinace_dialog import EditOrdinaceDialog
from models.ordinace import get_all_ordinace, add_ordinace, remove_ordinace, update_ordinace_db
from functools import partial
from models.rezervace import rezervace_pro_ordinaci

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
        self.add_ordinace_button.clicked.connect(self.add_ordinace)
        self.button_layout.addWidget(self.add_ordinace_button)
        self.layout.addLayout(self.button_layout)

        self.scroll = None  # <-- přidáno
        self.load_ordinace()

        # Styl pro všechny tabulky v tomto okně
        self.setStyleSheet("""
            QHeaderView::section {
                background-color: #9ee0fc;
                color: black;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton#remove_ordinace, 
            QPushButton#update_ordinace,
            QPushButton#change_password {
        min-width: 60px;
        max-width: 80px;
        min-height: 10px;
        max-height: 15px;
        padding: 2px 6px;
        font-size: 12px;
        border-style: outset;
        border-color: #b2d7ef;
        border-width: 1px;
        border-radius: 4px;
        background-color: #e6f7ff;
        color: #222;
        }
        QPushButton#change_password {
            background-color: #d0f0fd;
        }
        
        QPushButton#remove_ordinace:pressed,
        QPushButton#update_user:pressed,
        QPushButton#change_password:pressed {
           background-color: #b2d7ef;
            color: #000;
        }
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
            hbox.addWidget(label)                        

            remove_button = QPushButton("Odebrat")
            remove_button.setObjectName("remove_ordinace")
            remove_button.clicked.connect(partial(self.remove_ordinace, ord[0], ord[1]))
            update_button = QPushButton("Upravit")
            update_button.setObjectName("update_ordinace")
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
                print(data)
                add_ordinace(data)
                self.load_ordinace()
                if self.parent_window:
                    self.parent_window.status_bar.showMessage(f"Ordinace {data['nazev']} byl přidán.")
            except ValueError as ve:
                if self.parent_window:
                    self.parent_window.status_bar.showMessage(str(ve))
            except Exception as e:
                if self.parent_window:
                  self.parent_window.status_bar.showMessage(f"Chyba při přidávání ordinace: {e}")

    def remove_ordinace(self, ordinace_id, nazev):
        if QMessageBox.question(self, "Odebrat ordinaci", f"Opravdu chcete odebrat ordinaci {nazev}?", QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
            try:
              # Prohledat databazi, zda pro ordinaci neexistují rezervace
                rezervations_for_surgery = rezervace_pro_ordinaci(ordinace_id)
                if rezervations_for_surgery:
                    QMessageBox.warning(self, "Chyba", f"Ordinace {nazev} má existující rezervace a nemůže být odstraněna.")
                    return
                remove_ordinace(ordinace_id, nazev)
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
    
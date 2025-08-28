from PySide6.QtWidgets import QDialog, QVBoxLayout, QPushButton, QHBoxLayout, QMessageBox, QFrame, QTextEdit
from PySide6.QtWidgets import QWidget, QLabel, QPushButton, QHBoxLayout, QVBoxLayout, QScrollArea
from PySide6.QtCore import Qt
from views.add_doctor_dialog import AddDoctorDialog
from views.edit_doctor_dialog import EditDoctorDialog
from models.doktori import get_all_doctors, update_doctor, add_doctor, get_all_doctors_colors, get_doctor_by_id, check_doctor_reservations
from functools import partial
from controllers.data import basic_button_color, basic_button_style, q_header_view_style, basic_style

class DoctorDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Správa doktorů")
        self.resize(400, 350)
        self.center_to_parent()
        self.parent_window = parent

        self.layout = QVBoxLayout(self)

        self.button_layout = QHBoxLayout()
        self.add_doctor_button = QPushButton("Přidat doktora", self)
        self.add_doctor_button.setObjectName("add_doctor_button")
        self.add_doctor_button.setStyleSheet(f"background-color: {basic_button_color['add_button_color']};")
        self.add_doctor_button.clicked.connect(self.add_doctor)
        self.button_layout.addWidget(self.add_doctor_button)
        self.layout.addLayout(self.button_layout)

        self.scroll = None  # <-- přidáno
        self.load_doctors()
        
        # Styl pro všechny tabulky v tomto okně
        self.setStyleSheet(basic_style)
        self.setStyleSheet(f"""
        QHeaderView::section {{
            {q_header_view_style}
        }}
        QPushButton#remove_doctor, 
        QPushButton#update_doctor,
        QPushButton#add_doctor_button {{
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


    def load_doctors(self):
        # Odstraňte starý scroll area, pokud existuje
        if self.scroll is not None:
            self.layout.removeWidget(self.scroll)
            self.scroll.deleteLater()
            self.scroll = None
            
        self.users_widget = QWidget()
        vbox = QVBoxLayout(self.users_widget)
        doctors = get_all_doctors()
        for doctor in doctors:
            hbox = QHBoxLayout()
            label = QLabel(f"{doctor[1]} {doctor[2]}")
            label.setStyleSheet("font-weight: bold; font-size: 14px;")
            
            # Indikátor aktivního stavu
            # Ošetření None hodnoty pro is_active sloupec
            is_active_value = doctor[4]
            if is_active_value is None:
                is_active = True  # Výchozí hodnota pokud je NULL
            else:
                is_active = int(is_active_value) == 1
            active_indicator = QFrame()
            active_indicator.setFixedSize(24, 24)
            active_indicator.setStyleSheet(f"""
              background-color: {'#4CAF50' if is_active else '#F44336'};
              border-radius: 12px;
              border: 2px solid #888;
              margin-left: 8px;
              margin-right: 8px;
            """)
                        
            
            remove_button = QPushButton("Odebrat")
            remove_button.setObjectName("remove_doctor")
            remove_button.setStyleSheet(f"background-color: {basic_button_color['remove_button_color']};")
            remove_button.clicked.connect(partial(self.remove_doctor, doctor[0], doctor[1]))
            update_button = QPushButton("Upravit")
            update_button.setStyleSheet(f"background-color: {basic_button_color['update_button_color']};")
            update_button.setObjectName("update_doctor")
            update_button.clicked.connect(partial(self.update_doctor, doctor[0]))

            hbox.addWidget(label)
            hbox.addStretch(1)  # Přidá prázdný prostor mezi jméno a tlačítka
            # Přidá tlačítka pro odebrání a úpravu
            hbox.addWidget(remove_button)
            hbox.addWidget(update_button)
            hbox.addWidget(active_indicator)
            vbox.addLayout(hbox)
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setWidget(self.users_widget)
        self.layout.addWidget(self.scroll)

    def add_doctor(self):
        dialog = AddDoctorDialog(self)
        if dialog.exec() == QDialog.Accepted:
            try:
                data = dialog.get_data()
                add_doctor(data)
                self.load_doctors()
                if self.parent_window:
                    self.parent_window.status_bar.showMessage(f"Doktor {data['jmeno']} byl přidán.")
                if self.parent_window and hasattr(self.parent_window, "aktualizuj_doktori_layout"):
                      self.parent_window.aktualizuj_doktori_layout()
            except ValueError as ve:
                if self.parent_window:
                    self.parent_window.status_bar.showMessage(str(ve))
            except Exception as e:
                if self.parent_window:
                  self.parent_window.status_bar.showMessage(f"Chyba při přidávání doktora: {e}")
    
    def remove_doctor(self, doctor_id, username):
        # Nejdříve zkontrolujeme rezervace
        try:
            reservation_count = check_doctor_reservations(doctor_id)
            
            if reservation_count > 0:
                # Doktor má rezervace - nabídneme možnosti
                msg = QMessageBox(self)
                msg.setWindowTitle("Doktor má rezervace")
                msg.setText(f"Doktor {username} má {reservation_count} aktivních rezervací.")
                msg.setInformativeText("Vyberte možnost:")
                
                # Přidáme tlačítka
                deactivate_btn = msg.addButton("Deaktivovat doktora", QMessageBox.ActionRole)
                cancel_btn = msg.addButton("Zrušit", QMessageBox.RejectRole)
                
                msg.exec_()
                
                if msg.clickedButton() == deactivate_btn:
                    # Deaktivujeme doktora místo odstranění
                    try:
                        self.deactivate_doctor(doctor_id, username)
                    except Exception as e:
                        QMessageBox.critical(self, "Chyba", f"Chyba při deaktivaci doktora: {e}")
                # Jinak se nic neděje (Cancel)
                return
                
        except Exception as e:
            QMessageBox.critical(self, "Chyba", f"Chyba při kontrole rezervací: {e}")
            return
        
        # Doktor nemá rezervace - můžeme ho odstranit
        if QMessageBox.question(self, "Odebrat doktora", 
                               f"Opravdu chcete odebrat doktora {username}?", 
                               QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
            try:
                # Import funkce z modelu s jiným názvem pro vyhnuti konfliktu
                from models.doktori import remove_doctor as remove_doctor_from_db
                remove_doctor_from_db(doctor_id)
                self.load_doctors()
                if self.parent_window:
                    self.parent_window.status_bar.showMessage(f"Doktor {username} byl odstraněn.")
            except Exception as e:
                QMessageBox.critical(self, "Chyba", f"Chyba při odstraňování doktora: {e}")

    def deactivate_doctor(self, doctor_id, username):
        """Deaktivuje doktora místo odstranění."""
        try:
            from models.doktori import update_doctor as update_doctor_in_db, get_doctor_by_id
            
            # Nejdříve získáme aktuální data doktora
            doctor_data = get_doctor_by_id(doctor_id)
            if not doctor_data:
                raise ValueError("Doktor nebyl nalezen.")
            
            # Připravíme kompletní data s aktualizovaným isActive
            update_data = {
                'jmeno': doctor_data[1],         # jmeno
                'prijmeni': doctor_data[2],      # prijmeni
                'specializace': doctor_data[3],  # specializace
                'isActive': 0,                   # deaktivujeme
                'color': doctor_data[5]          # color
            }
            
            # Poznámka: update_doctor očekává (data, doktor_id)
            update_doctor_in_db(update_data, doctor_id)
            self.load_doctors()
            if self.parent_window:
                self.parent_window.status_bar.showMessage(f"Doktor {username} byl deaktivován.")
        except Exception as e:
            raise e

    def update_doctor(self, doctor_id):
        # Najděte aktuální roli doktora
        doctors = get_all_doctors()
        doctor = next((u for u in doctors if u[0] == doctor_id), None)
        if not doctor:
            if self.parent_window:
                self.parent_window.status_bar.showMessage("Uživatel nenalezen.")
            return
        doctor_id = doctor[0]
        dialog = EditDoctorDialog(doctor_id)
        if dialog.exec() == QDialog.Accepted:
            data = dialog.get_data()
            try: 
                update_doctor(data, doctor_id)
                if self.parent_window and hasattr(self.parent_window, "aktualizuj_doktori_layout"):
                      self.parent_window.aktualizuj_doktori_layout()
                      self.parent_window.nacti_rezervace()
                self.load_doctors()
                if self.parent_window:
                    self.parent_window.status_bar.showMessage(f"Doktor {data['jmeno']} {data['prijmeni']} upraven/a.")
            except Exception as e:
                if self.parent_window:
                    self.parent_window.status_bar.showMessage(f"Chyba při úpravě doktora: {e}")
    
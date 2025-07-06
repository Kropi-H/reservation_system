from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QSpinBox, QSlider, QDialogButtonBox, QMessageBox
from PySide6.QtCore import Qt
from models.settings import get_settings, save_settings
from models.rezervace import smaz_rezervace_starsi_nez
from controllers.data import basic_style

class SmazRezervaceDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Zrušení rezervací")
        self.setFixedSize(350, 250)

        self.days_to_keep = int(get_settings("days_to_keep"))

        # Jednoduché stylování
        self.setStyleSheet(basic_style)

        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(15, 15, 15, 15)

        # Hlavní label
        self.label = QLabel(f"Zadejte počet dní pro smazání rezervací:\nPokud je 0, rezervace se mazat nebudou.\nAktuální nastavení: {self.days_to_keep} dní.")
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setWordWrap(True)
        layout.addWidget(self.label)

        # SpinBox
        spinbox_layout = QHBoxLayout()
        spinbox_label = QLabel("Počet dní:")
        
        self.days_input = QSpinBox()
        self.days_input.setMinimum(0)
        self.days_input.setMaximum(365)
        self.days_input.setValue(self.days_to_keep)
        self.days_input.setSuffix(" dní")
        
        spinbox_layout.addWidget(spinbox_label)
        spinbox_layout.addWidget(self.days_input)
        layout.addLayout(spinbox_layout)

        # Slider
        self.days_slider = QSlider(Qt.Horizontal)
        self.days_slider.setMinimum(0)
        self.days_slider.setMaximum(365)
        self.days_slider.setValue(self.days_to_keep)
        layout.addWidget(self.days_slider)

        # Tlačítka
        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.button_box.button(QDialogButtonBox.Ok).setText("Potvrdit")
        self.button_box.button(QDialogButtonBox.Cancel).setText("Zrušit")
        layout.addWidget(self.button_box)

        # Propojení signálů
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        
        # Synchronizace mezi spinboxem a sliderem
        self.days_input.valueChanged.connect(self.days_slider.setValue)
        self.days_slider.valueChanged.connect(self.days_input.setValue)

    def get_days(self):
        """Vrátí počet dní pro uchování rezervací."""
        return self.days_input.value()
    
    def set_days_to_keep(self):
        """Nastaví počet dní pro uchování rezervací."""
        try:
            days = self.days_input.value()
            if days <= 0:
                raise ValueError("Data se nebudou mazat, protože počet dní je 0.")
            self.days_input.setValue(days)
            self.days_slider.setValue(days)
            save_settings({"days_to_keep": str(days)})
            result = smaz_rezervace_starsi_nez(days)
            return result
        except ValueError as e:
             QMessageBox.information(
                      self,
                      "Zpráva:",
                      f"{e}"
                  )
             return None
            
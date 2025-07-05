from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QSpinBox, QSlider, QDialogButtonBox
from PySide6.QtCore import Qt
from models.settings import get_settings, save_settings
from models.rezervace import smaz_rezervace_starsi_nez

class SmazRezervaceDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Zrušení rezervací")
        self.setFixedSize(350, 250)

        self.days_to_keep = int(get_settings("days_to_keep"))

        # Jednoduché stylování
        self.setStyleSheet("""
            QDialog {
                background-color: #f5f5f5;
                font-family: Arial, sans-serif;
            }
            QLabel {
                color: #333;
                font-size: 12px;
                padding: 5px;
            }
            QSpinBox {
                border: 1px solid #ccc;
                border-radius: 3px;
                padding: 5px;
                font-size: 14px;
                background-color: white;
            }
            QSpinBox:focus {
                border-color: #0078d4;
            }
            QSlider::groove:horizontal {
                border: 1px solid #ccc;
                height: 6px;
                background: #e0e0e0;
                border-radius: 3px;
            }
            QSlider::handle:horizontal {
                background: #0078d4;
                border: 1px solid #005a9e;
                width: 16px;
                height: 16px;
                border-radius: 8px;
                margin: -5px 0;
            }
            QSlider::sub-page:horizontal {
                background: #0078d4;
                border-radius: 3px;
            }
            QPushButton {
                background-color: #0078d4;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 3px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #106ebe;
            }
        """)

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
            self.days_input.setValue(days)
            self.days_slider.setValue(days)
            save_settings({"days_to_keep": str(days)})
            result = smaz_rezervace_starsi_nez(days)
            return result
        except ValueError as e:
            print(f"Chyba při nastavování počtu dní: {e}")
            return None
            # Můžete přidat další zpracování chyby, např. zobrazit dialog s chybou
from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QComboBox

class AddOrdinaceDialog(QDialog):
    def __init__(self, ordinace_id, parent=None):
        super().__init__(parent)
        self.ordinace_id = ordinace_id
        self.setWindowTitle("Upravit Ordinaci")
        self.setGeometry(100, 100, 400, 300)
        self.layout = QVBoxLayout(self)

        # Form fields for editing ordinace
        self.nazev_ordinace_input = QLineEdit(self)
        self.nazev_ordinace_input.setPlaceholderText("Název ordinace")
        self.layout.addWidget(self.nazev_ordinace_input)

        self.ordinace_patro_input = QLineEdit(self)
        self.ordinace_patro_input.setPlaceholderText("Patro ordinace")
        self.layout.addWidget(self.ordinace_patro_input)

        self.popis_ordinace_input = QLineEdit(self)
        self.popis_ordinace_input.setPlaceholderText("Popis ordinace")
        self.layout.addWidget(self.popis_ordinace_input)

        # Buttons
        button_layout = QHBoxLayout()
        save_button = QPushButton("Uložit", self)
        save_button.clicked.connect(self.accept)
        button_layout.addWidget(save_button)

        cancel_button = QPushButton("Zrušit", self)
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)

        self.layout.addLayout(button_layout)

    def get_data(self):
        return {
            "ordinace_id": self.ordinace_id,
            "nazev": self.nazev_ordinace_input.text(),
            "patro": self.ordinace_patro_input.text(),
            "popis": self.popis_ordinace_input.text()
        }
    def set_data(self, data):
        self.nazev_ordinace_input.setText(data.get("nazev", ""))
        self.ordinace_patro_input.setText(data.get("patro", ""))
        self.popis_ordinace_input.setText(data.get("popis", ""))
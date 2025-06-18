from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QComboBox

class AddOrdinaceDialog(QDialog):
    def __init__(self, ordinace_id, parent=None):
        super().__init__(parent)
        self.ordinace_id = ordinace_id
        self.setWindowTitle("Přidat ordinaci")
        layout = QVBoxLayout(self)

        # Form fields for editing ordinace
        layout.addWidget(QLabel("Název ordinace:"))
        self.nazev_ordinace_input = QLineEdit(self)
        self.nazev_ordinace_input.setPlaceholderText("Název ordinace")
        layout.addWidget(self.nazev_ordinace_input)

        layout.addWidget(QLabel("Patro:"))
        self.ordinace_patro_input = QComboBox(self)
        self.ordinace_patro_input.addItems(["0", "1"])  # Assuming a maximum of 5 patra
        layout.addWidget(self.ordinace_patro_input)

        layout.addWidget(QLabel("Popis:"))
        self.popis_ordinace_input = QLineEdit(self)
        self.popis_ordinace_input.setPlaceholderText("Popis ordinace")
        layout.addWidget(self.popis_ordinace_input)

        # Buttons
        button_layout = QHBoxLayout()
        save_button = QPushButton("Uložit", self)
        save_button.clicked.connect(self.accept)
        button_layout.addWidget(save_button)

        cancel_button = QPushButton("Zrušit", self)
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)

        layout.addLayout(button_layout)

    def get_data(self):
        if not self.nazev_ordinace_input.text() or not self.ordinace_patro_input.currentText() or not self.popis_ordinace_input.text():
            raise ValueError("Všechna pole musí být vyplněna.") 
        return {
            "nazev": self.nazev_ordinace_input.text(),
            "patro": int(self.ordinace_patro_input.currentText()),
            "popis": self.popis_ordinace_input.text()
        }
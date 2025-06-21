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
        save_button.clicked.disconnect()
        save_button.clicked.connect(self.try_accept)
        button_layout.addWidget(save_button)

        cancel_button = QPushButton("Zrušit", self)
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)

        layout.addLayout(button_layout)
        
    def check_fields(self):
        # Check if all fields are filled
        if not self.nazev_ordinace_input.text():
            self.nazev_ordinace_input.setPlaceholderText("Název ordinace je povinný")
            self.nazev_ordinace_input.setStyleSheet("color: red;")
            return False
        if not self.popis_ordinace_input.text():
            self.popis_ordinace_input.setPlaceholderText("Popis ordinace je povinný")
            self.popis_ordinace_input.setStyleSheet("color: red;")
            return False
        return True
      
    def try_accept(self):
        if self.check_fields():
            self.accept()
        else:
            self.nazev_ordinace_input.setFocus()

    def get_data(self):
        if not self.check_fields():
            raise ValueError("Všechna pole musí být vyplněna.")
        # Return the data as a dictionary
        return {
            "nazev": self.nazev_ordinace_input.text(),
            "patro": int(self.ordinace_patro_input.currentText()),
            "popis": self.popis_ordinace_input.text()
        }
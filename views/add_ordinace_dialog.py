

class AddOrdinaceDialog(QDialog):
    def __init__(self, ordinace_id, parent=None):
        super().__init__(parent)
        self.ordinace_id = ordinace_id
        self.setWindowTitle("Upravit Ordinaci")
        self.setGeometry(100, 100, 400, 300)
        self.layout = QVBoxLayout(self)

        # Form fields for editing ordinace
        self.username_input = QLineEdit(self)
        self.username_input.setPlaceholderText("Uživatelské jméno")
        self.layout.addWidget(self.username_input)

        self.jmeno_input = QLineEdit(self)
        self.jmeno_input.setPlaceholderText("Jméno")
        self.layout.addWidget(self.jmeno_input)

        self.prijmeni_input = QLineEdit(self)
        self.prijmeni_input.setPlaceholderText("Příjmení")
        self.layout.addWidget(self.prijmeni_input)

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
            "username": self.username_input.text(),
            "jmeno": self.jmeno_input.text(),
            "prijmeni": self.prijmeni_input.text()
        }
    def set_data(self, data):
        self.username_input.setText(data.get("username", ""))
        self.jmeno_input.setText(data.get("jmeno", ""))
        self.prijmeni_input.setText(data.get("prijmeni", ""))
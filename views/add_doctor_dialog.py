from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QComboBox, QColorDialog, QTextEdit
from models.doktori import get_doctor_by_id  # Assuming this function retrieves a list of doctors
from PySide6.QtGui import QColor

class AddDoctorDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Přidat doktora")
        self.setModal(True)
        self.layout = QVBoxLayout(self)

        self.layout.addWidget(QLabel("Jméno doktora:"))
        self.username_add = QLineEdit()
        self.layout.addWidget(self.username_add)

        self.layout.addWidget(QLabel("Příjmení doktora:"))
        self.prijmeni_add = QLineEdit()
        self.layout.addWidget(self.prijmeni_add)

        self.layout.addWidget(QLabel("Specializace:"))
        self.specializace_add = QTextEdit()
        self.layout.addWidget(self.specializace_add)

        self.layout.addWidget(QLabel("Aktivní:"))
        self.is_active_combo = QComboBox()  # Assuming you have a predefined list of active states
        self.is_active_combo.addItems(["Ano", "Ne"])
        self.layout.addWidget(self.is_active_combo)

        # Výběr barvy
        color_layout = QHBoxLayout()
        color_label = QLabel("Barva:")
        color_layout.addWidget(color_label)
        self.color_button = QPushButton("Vybrat barvu")
        self.color_button.clicked.connect(self.choose_color)
        color_layout.addWidget(self.color_button)
        self.selected_color = QColor("#ffffff")
        self.color_preview = QLabel()
        self.color_preview.setFixedSize(40, 20)
        self.color_preview.setStyleSheet(f"background-color: {self.selected_color.name()}; border: 1px solid #888;")
        color_layout.addWidget(self.color_preview)
        self.layout.addLayout(color_layout)

        button_layout = QHBoxLayout()
        self.ok_button = QPushButton("Přidat")
        self.ok_button.clicked.connect(self.accept)
        self.cancel_button = QPushButton("Zrušit")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)
        self.layout.addLayout(button_layout)

    def choose_color(self):
        color = QColorDialog.getColor(self.selected_color, self, "Vyberte barvu")
        if color.isValid():
            self.selected_color = color
            self.color_preview.setStyleSheet(f"background-color: {color.name()}; border: 1px solid #888;")

    def get_data(self):
        if not self.username_add.text() or not self.prijmeni_add.text() or not self.specializace_add.toPlainText():
            raise ValueError("Všechna pole musí být vyplněna.")
        return {
            "jmeno": self.username_add.text(),
            "prijmeni": self.prijmeni_add.text(),
            "specializace": self.specializace_add.toPlainText(),
            "isActive": 1 if self.is_active_combo.currentText() == "Ano" else 0,
            "color": self.selected_color.name()
        }
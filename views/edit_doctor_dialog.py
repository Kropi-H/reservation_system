from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QComboBox, QColorDialog
from models.doktori import get_doctor_by_id
from PySide6.QtGui import QColor


class EditDoctorDialog(QDialog):
    def __init__(self, doctor_id, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Upravit doktora")
        layout = QVBoxLayout(self)
        self.doctor = get_doctor_by_id(doctor_id)  # Assuming this function retrieves a doctor's details by ID

        layout.addWidget(QLabel("Jméno doktora:"))
        self.username_edit = QLineEdit(self.doctor[1])
        layout.addWidget(self.username_edit)
        
        layout.addWidget(QLabel("Příjmení doktora:"))
        self.prijmeni_add = QLineEdit(self.doctor[2])
        layout.addWidget(self.prijmeni_add)
        
        layout.addWidget(QLabel("Specializace:"))
        self.specializace_add = QLineEdit(self.doctor[3])
        layout.addWidget(self.specializace_add)

        layout.addWidget(QLabel("Aktivní:"))
        self.is_active_combo = QComboBox()  # Assuming you have a predefined list of active states
        self.is_active_combo.addItems(["Ano", "Ne"] if self.doctor[4] == 1 else ["Ne", "Ano"])  # Assuming the active state is in the 4th column
        layout.addWidget(self.is_active_combo)
        
        # Výběr barvy
        color_layout = QHBoxLayout()
        color_label = QLabel("Barva:")
        color_layout.addWidget(color_label)
        self.color_button = QPushButton("Vybrat barvu")
        self.color_button.clicked.connect(self.choose_color)
        color_layout.addWidget(self.color_button)
        self.selected_color = QColor(self.doctor[5])  # Assuming the color is stored in the 5th column
        self.color_preview = QLabel()
        self.color_preview.setFixedSize(40, 20)
        self.color_preview.setStyleSheet(f"background-color: {self.selected_color.name()}; border: 1px solid #888;")
        color_layout.addWidget(self.color_preview)
        layout.addLayout(color_layout)

        button_layout = QHBoxLayout()
        ok_button = QPushButton("Uložit")
        ok_button.clicked.connect(self.accept)
        cancel_button = QPushButton("Zrušit")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)

    def choose_color(self):
        color = QColorDialog.getColor(self.selected_color, self, "Vyberte barvu")
        if color.isValid():
            self.selected_color = color
            self.color_preview.setStyleSheet(f"background-color: {color.name()}; border: 1px solid #888;")

    def get_data(self):
        return {
            "jmeno": self.username_edit.text(),
            "prijmeni": self.prijmeni_add.text(),
            "specializace": self.specializace_add.text(),
            "isActive": 1 if self.is_active_combo.currentText() == "Ano" else 0,
            "color": self.selected_color.name()
        } 
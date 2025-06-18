from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QComboBox, QColorDialog
from models.ordinace import get_ordinace_by_id
from PySide6.QtGui import QColor


class EditOrdinaceDialog(QDialog):
    def __init__(self, ordinace_id, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Upravit ordinaci")
        layout = QVBoxLayout(self)
        self.ordinace = get_ordinace_by_id(ordinace_id)  # Assuming this function retrieves a doctor's details by ID

        layout.addWidget(QLabel("Název ordinace:"))
        self.ordinace_nazev = QLineEdit(self.ordinace[1])
        layout.addWidget(self.ordinace_nazev)
        
        layout.addWidget(QLabel("Patro:"))
        self.ordinace_patro = QComboBox()
        self.ordinace_patro.addItems(["0", "1"])
        self.ordinace_patro.setCurrentText(str(self.ordinace[2]))
        layout.addWidget(self.ordinace_patro)
        
        layout.addWidget(QLabel("Popis:"))
        self.popis_ordinace = QLineEdit(self.ordinace[3])
        layout.addWidget(self.popis_ordinace)
        

        button_layout = QHBoxLayout()
        ok_button = QPushButton("Uložit")
        ok_button.clicked.connect(self.accept)
        cancel_button = QPushButton("Zrušit")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)

    def get_data(self):
        return {
            "nazev": self.ordinace_nazev.text(),
            "patro": int(self.ordinace_patro.currentText()),
            "popis": self.popis_ordinace.text()
        } 
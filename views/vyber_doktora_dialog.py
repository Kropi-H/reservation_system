from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QComboBox, QPushButton
from models.databaze import get_doktori
from controllers.data import basic_style

class VyberDoktoraDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        # Handle both dictionary (PostgreSQL) and tuple (SQLite) formats
        doktori_data = get_doktori()
        
        if doktori_data and isinstance(doktori_data[0], dict):
            # PostgreSQL format - use dictionary keys with whitespace normalization
            self.doktori = [' '.join(f"{d['jmeno']} {d['prijmeni']}".split()) for d in doktori_data]
        else:
            # SQLite format - use index access with whitespace normalization
            self.doktori = [' '.join(f"{d[1]} {d[2]}".split()) for d in doktori_data]
            
        self.setWindowTitle("Výběr doktora")
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Vyberte doktora pro zvolené časy:"))
        self.combo = QComboBox()
        self.combo.addItems(self.doktori)
        self.setStyleSheet(basic_style)
        layout.addWidget(self.combo)
        btn_ok = QPushButton("Potvrdit")
        btn_ok.clicked.connect(self.accept)
        layout.addWidget(btn_ok)
        btn_cancel = QPushButton("Zrušit")
        btn_cancel.clicked.connect(self.reject)
        layout.addWidget(btn_cancel)

    def get_selected(self):
        return self.combo.currentText()
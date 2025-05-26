from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QComboBox, QPushButton

class VyberDoktoraDialog(QDialog):
    def __init__(self, doktori, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Výběr doktora")
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Vyberte doktora pro zvolené časy:"))
        self.combo = QComboBox()
        self.combo.addItems(doktori)
        layout.addWidget(self.combo)
        btn_ok = QPushButton("Potvrdit")
        btn_ok.clicked.connect(self.accept)
        layout.addWidget(btn_ok)
        btn_cancel = QPushButton("Zrušit")
        btn_cancel.clicked.connect(self.reject)
        layout.addWidget(btn_cancel)

    def get_selected(self):
        return self.combo.currentText()
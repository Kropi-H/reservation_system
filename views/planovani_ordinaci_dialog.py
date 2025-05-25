from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton

class PlanovaniOrdinaciDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Plánování ordinací")
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Chcete zahájit plánování ordinací?"))
        btn_ok = QPushButton("Ano")
        btn_cancel = QPushButton("Zrušit")
        btn_ok.clicked.connect(self.accept)
        btn_cancel.clicked.connect(self.reject)
        layout.addWidget(btn_ok)
        layout.addWidget(btn_cancel)
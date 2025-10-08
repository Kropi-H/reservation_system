from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QDialogButtonBox
from PySide6.QtCore import Qt
from controllers.data import basic_style

class PatientStatusDialog(QDialog):
    def __init__(self, reservation_data, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Stav pacienta")
        self.setFixedSize(350, 250)
        self.reservation_data = reservation_data
        self.selected_status = None
        
        # Hlavní layout
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        # Informace o rezervaci
        print(reservation_data)
        info_label = QLabel(f"Majitel: {reservation_data[4]}\nPacient/Problem: {reservation_data[3]}")
        info_label.setAlignment(Qt.AlignCenter)
        info_label.setStyleSheet("font-weight: bold; font-size: 14px; padding: 10px;")
        layout.addWidget(info_label)
        
        # Tlačítka pro stav
        buttons_layout = QVBoxLayout()
        buttons_layout.setSpacing(10)
        
        # Tlačítko "PACIENT V ČEKÁRNĚ"
        ceka_button = QPushButton("PACIENT V ČEKÁRNĚ")
        ceka_button.setMinimumHeight(40)
        ceka_button.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                font-weight: bold;
                font-size: 12px;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        ceka_button.clicked.connect(lambda: self.set_status("ceka"))
        buttons_layout.addWidget(ceka_button)
        
        # Tlačítko "PACIENT ODBAVEN"
        odbaven_button = QPushButton("PACIENT ODBAVEN")  
        odbaven_button.setMinimumHeight(40)
        odbaven_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-weight: bold;
                font-size: 12px;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        odbaven_button.clicked.connect(lambda: self.set_status("odbaven"))
        buttons_layout.addWidget(odbaven_button)
        
        # Tlačítko "NULOVÁNÍ STAVU"
        null_button = QPushButton("NULOVÁNÍ STAVU")
        null_button.setMinimumHeight(40)
        null_button.setStyleSheet("""
            QPushButton {
                background-color: #FF9800;
                color: white;
                font-weight: bold;
                font-size: 12px;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #F57C00;
            }
        """)
        null_button.clicked.connect(lambda: self.set_status(None))
        buttons_layout.addWidget(null_button)
        
        layout.addLayout(buttons_layout)
        
        # Standardní tlačítka dialogu (Zrušit)
        button_box = QDialogButtonBox(QDialogButtonBox.Cancel)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        self.setStyleSheet(basic_style)
    
    def set_status(self, status):
        """Nastaví vybraný stav a zavře dialog"""
        self.selected_status = status
        self.accept()
    
    def get_selected_status(self):
        """Vrátí vybraný stav"""
        return self.selected_status
from PySide6.QtWidgets import QStyledItemDelegate
from PySide6.QtCore import Qt, QRect
from PySide6.QtGui import QPainter, QColor, QPen

class TimeCellDelegate(QStyledItemDelegate):
    def __init__(self, parent=None):
        super().__init__(parent)
    
    def paint(self, painter, option, index):
        # Nejprve vykreslíme standardní obsah buňky
        super().paint(painter, option, index)
        
        # Získáme barvy doktorů z dat modelu
        doctor_colors = index.data(Qt.UserRole)
        
        if doctor_colors and len(doctor_colors) > 0:
            # Nastavíme kreslení
            painter.setRenderHint(QPainter.Antialiasing, True)
            
            # Definujeme parametry kolečka
            circle_radius = 5
            circle_spacing = 14
            margin = 6
            
            # Vypočítáme pozici pro kolečka (pravý dolní roh)
            rect = option.rect
            start_x = rect.right() - margin - (circle_radius * 2)
            start_y = rect.bottom() - margin - (circle_radius * 2)
            
            # Vykreslíme kolečka podle barev doktorů
            # První doktor vlevo, druhý doktor vpravo
            for i, color_str in enumerate(doctor_colors[:2]):  # Maximum 2 kolečka
                if color_str and color_str.strip():
                    # i=0 (první doktor) → pozice 1 (vlevo), i=1 (druhý doktor) → pozice 0 (vpravo)
                    if i == 0:  # První doktor vlevo
                        position = 1 if len(doctor_colors) > 1 else 0
                    else:  # Druhý doktor vpravo
                        position = 0
                    x = start_x - (position * circle_spacing)
                    y = start_y
                    
                    # Převedeme barvu na QColor
                    try:
                        color = QColor(color_str.strip())
                        if not color.isValid():
                            color = QColor("#999999")  # Fallback barva
                    except:
                        color = QColor("#999999")  # Fallback barva
                    
                    # Vykreslíme kolečko s černým okrajem
                    painter.setPen(QPen(QColor("#636363"), 1.5))
                    painter.setBrush(color)
                    painter.drawEllipse(x, y, circle_radius * 2, circle_radius * 2)
    
    def sizeHint(self, option, index):
        # Zachováme původní velikost
        return super().sizeHint(option, index)
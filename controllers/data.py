table_grey_strip = "#f0f0f0" # barva šedého pruhu
vaccination_color = "#d0d4ec" # barva vakcinace
pause_color = "#e8e500" # barva pauzy
anesthesia_color = "#ffc774" # barva anestezie

basic_button_color = {
    "update_password_button_color": "#fbff90", # barva přidat doktora tlačítko
    "add_button_color": "#a9d386", # barva přidat tlačítko
    "remove_button_color": "#F3B0B0", # barva odstranit tlačítko
    "update_button_color": "#cde7ff", # barva aktualizovat tlačítko
}

button_border_radius = 2 # rádius, tlačítek

basic_button_style = f"""
    min-width: 60px;
    max-width: 100px;
    min-height: 10px;
    max-height: 20px;
    padding: 2px 6px;
    margin: 2px;
    font-weight: bold;
    font-size: 12px;
    border-style: outset;
    border-color: #b2d7ef;
    border-width: 1px;
    border-radius: {button_border_radius}px;
    """
    
q_header_view_style = f"""
    background-color: #9ee0fc;
    color: black;
    font-weight: bold;
    font-size: 14px;
    """
    
basic_style = f"""
            QDialog {{
                background-color: #f5f5f5;
                font-family: Arial, sans-serif;
            }}
            QLabel {{
                color: #333;
                font-size: 12px;
                padding: 5px;
            }}
            QSpinBox {{
                border: 1px solid #ccc;
                border-radius: 3px;
                padding: 5px;
                font-size: 14px;
                background-color: white;
            }}
            QSpinBox:focus {{
                border-color: #0078d4;
            }}
            QSlider::groove:horizontal {{
                border: 1px solid #ccc;
                height: 6px;
                background: #e0e0e0;
                border-radius: 3px;
            }}
            QSlider::handle:horizontal {{
                background-color: #0078d4;
                border: 1px solid #005a9e;
                width: 16px;
                height: 16px;
                border-radius: 8px;
                margin: -5px 0;
            }}
            QSlider::sub-page:horizontal {{
                background-color: #0078d4;
                border-radius: 3px;
            }}
            QPushButton {{
                background-color: #0078d4;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 3px;
                font-size: 12px;
            }}
            QPushButton:hover {{
                background-color: #106ebe;
            }}
        """
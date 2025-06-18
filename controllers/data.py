table_grey_strip = "#f0f0f0" # barva šedého pruhu
vaccination_color = "#d0d4ec" # barva vakcinace
pause_color = "#e8e500" # barva pauzy

basic_button_color = {
    "update_password_button_color": "#eeff90", # barva přidat doktora tlačítko
    "add_button_color": "#c2fa94", # barva přidat tlačítko
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
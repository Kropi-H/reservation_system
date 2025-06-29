from models.users import get_all_users
from models.users import insert_admin_user
from views.set_admin_dialog import SetAdminDialog
from PySide6.QtWidgets import QDialog

def setup_admin():
    # Vložení admina do databáze
    user = get_all_users()
    
    if not user:
        # Pokud není žádný uživatel, vlož admina
        dialog = SetAdminDialog()
        try:
            result = dialog.exec()
            if result == QDialog.Accepted:
                data = dialog.return_data()
                if data:
                    
                    insert_admin_user(data["name"], data["password"])
                    
                    return True
                else:
                    print("Neplatná data, admin nebyl vložen.")
                    return False
            else:
                
                return False
        except Exception as e:
            print(f"Chyba při vkládání admina: {e}")
            return False
    else:
        return True
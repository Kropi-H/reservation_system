from PySide6.QtWidgets import QDialog, QVBoxLayout, QPushButton, QHBoxLayout, QMessageBox
from PySide6.QtWidgets import QWidget, QLabel, QPushButton, QHBoxLayout, QVBoxLayout, QScrollArea
from views.add_user_dialog import AddUserDialog
from models.users import get_all_users, add_user, remove_user, update_user
from functools import partial

class UsersDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Správa uživatelů")
        self.resize(400, 350)
        self.center_to_parent()
        self.setStyleSheet(""" ... """)
        self.parent_window = parent

        self.layout = QVBoxLayout(self)

        self.button_layout = QHBoxLayout()
        self.add_user_button = QPushButton("Přidat uživatele", self)
        self.add_user_button.clicked.connect(self.add_user)
        self.button_layout.addWidget(self.add_user_button)
        self.layout.addLayout(self.button_layout)

        self.scroll = None  # <-- přidáno
        self.load_users()
        
        # Styl pro všechny tabulky v tomto okně
        self.setStyleSheet("""
            QTableWidget {
                background-color: #fafdff;
                font-size: 15px;
                color: #222;
                gridline-color: #b2d7ef;
                selection-background-color: #cceeff;
                selection-color: #000;
            }
            QTableWidgetItem {
                margin: 10px;
                padding: 6px;
            }
            QHeaderView::section {
                background-color: #9ee0fc;
                color: black;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton#remove_user, 
            QPushButton#update_user,
            QPushButton#change_password {
        min-width: 60px;
        max-width: 80px;
        min-height: 10px;
        max-height: 15px;
        padding: 2px 6px;
        font-size: 12px;
        border-style: outset;
        border-color: #b2d7ef;
        border-width: 1px;
        border-radius: 4px;
        background-color: #e6f7ff;
        color: #222;
        }
        QPushButton#change_password {
            background-color: #d0f0fd;
        }
        
        QPushButton#remove_user:pressed,
        QPushButton#update_user:pressed,
        QPushButton#change_password:pressed {
           background-color: #b2d7ef;
            color: #000;
        }
        """)  
 
        
    def center_to_parent(self):
        if self.parent():
            parent_geom = self.parent().geometry()
            self_geom = self.geometry()
            x = parent_geom.x() + (parent_geom.width() - self_geom.width()) // 2
            y = parent_geom.y() + (parent_geom.height() - self_geom.height()) // 2
            self.move(x, y)


    def load_users(self):
        # Odstraňte starý scroll area, pokud existuje
        if self.scroll is not None:
            self.layout.removeWidget(self.scroll)
            self.scroll.deleteLater()
            self.scroll = None
            
        self.users_widget = QWidget()
        vbox = QVBoxLayout(self.users_widget)
        users = get_all_users()
        for user in users:
            hbox = QHBoxLayout()
            label = QLabel(f"{user[1]} ({user[3]})")
            hbox.addWidget(label)
            if user[3] == 'admin':
                remove_button = QPushButton("Chráněno")
                remove_button.setObjectName("remove_user")
                remove_button.setEnabled(False)
                update_button = QPushButton("Chráněno")
                update_button.setObjectName("update_user")
                update_button.setEnabled(False)
                password_button = QPushButton("Chráněno")
                password_button.setObjectName("change_password")
                password_button.setEnabled(False)
            else:
                remove_button = QPushButton("Odebrat")
                remove_button.setObjectName("remove_user")
                remove_button.clicked.connect(partial(self.remove_user, user[0], user[1]))
                update_button = QPushButton("Upravit")
                update_button.setObjectName("update_user")
                update_button.clicked.connect(partial(self.update_user, user[0], user[1]))
                password_button = QPushButton("Heslo")
                password_button.setObjectName("change_password")
                password_button.clicked.connect(partial(self.change_password, user[0], user[1]))
            hbox.addWidget(remove_button)
            hbox.addWidget(update_button)
            hbox.addWidget(password_button)
            vbox.addLayout(hbox)
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setWidget(self.users_widget)
        self.layout.addWidget(self.scroll)

    def add_user(self):
        dialog = AddUserDialog(self)
        if dialog.exec() == QDialog.Accepted:
            data = dialog.get_data()
            try:
                add_user(data)
                self.load_users()
                if self.parent_window:
                    self.parent_window.status_bar.showMessage(f"Uživatel {data['username']} byl přidán.")
            except Exception as e:
                QMessageBox.critical(self, "Chyba", f"Chyba při přidávání uživatele: {e}")
    
    def remove_user(self, user_id, username):
        if QMessageBox.question(self, "Odebrat uživatele", f"Opravdu chcete odebrat uživatele {username}?", QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
            try:
                remove_user(user_id, username)
                #QMessageBox.information(self, "Úspěch", result)
                self.load_users()
                if self.parent_window:
                    self.parent_window.status_bar.showMessage(f"Uživatel {username} byl odebrán.")
            except Exception as e:
                QMessageBox.critical(self, "Chyba", f"Chyba při odstraňování uživatele: {e}")

    def update_user(self, user_id, username):
        # Logic to update user details (show a dialog to edit user details)
        print(f"Update user {username} with ID {user_id}")
    
    def change_password(self, user_id, username):
        # Logic to change user password (show a dialog to enter new password)
        print(f"Change password for user {username} with ID {user_id}")
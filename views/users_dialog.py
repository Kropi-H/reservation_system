from PySide6.QtWidgets import QDialog, QVBoxLayout, QTableWidget, QTableWidgetItem, QPushButton, QHBoxLayout, QMessageBox
from models.users import get_all_users, add_user, remove_user, update_user
from functools import partial

class UsersDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Správa uživatelů")
        self.resize(500, 350)  # Základní velikost okna (šířka, výška)
        self.center_to_parent()
        
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
            QPushButton {
        min-width: 80px;
        max-width: 120px;
        padding: 2px 6px;
        font-size: 12px;
        border: 1px solid #009688;
        background-color: #e6f7ff;
        color: #222;
        }
        """)  

        self.parent_window = parent  # Store the parent window reference

        self.layout = QVBoxLayout(self)

        self.user_table = QTableWidget(self)
        self.user_table.setColumnCount(4)
        self.user_table.setHorizontalHeaderLabels(["Uživatel", "Role", "Smazat", "Upravit"])
        self.user_table.setColumnWidth(2, 150)  # Akce (tlačítko)
        self.user_table.setColumnWidth(3, 150)  # Akce (tlačítko)
        self.layout.addWidget(self.user_table)

        self.load_users()

        self.button_layout = QHBoxLayout()
        self.add_user_button = QPushButton("Přidat uživatele", self)
        self.add_user_button.clicked.connect(self.add_user)
        self.button_layout.addWidget(self.add_user_button)

        '''self.remove_user_button = QPushButton("Odebrat uživatele", self)
        self.remove_user_button.clicked.connect(self.remove_user)
        self.button_layout.addWidget(self.remove_user_button)'''

        ''' self.update_user_button = QPushButton("Upravit uživatele", self)
        self.update_user_button.clicked.connect(self.update_user)
        self.button_layout.addWidget(self.update_user_button)'''

        self.layout.addLayout(self.button_layout)
        
    def center_to_parent(self):
        if self.parent():
            parent_geom = self.parent().geometry()
            self_geom = self.geometry()
            x = parent_geom.x() + (parent_geom.width() - self_geom.width()) // 2
            y = parent_geom.y() + (parent_geom.height() - self_geom.height()) // 2
            self.move(x, y)

    def load_users(self):
        self.user_table.setRowCount(0)
        users = get_all_users()
        for user in users:
            user_id = user[0]
            username = user[1]
            row_position = self.user_table.rowCount()
            self.user_table.insertRow(row_position)
            self.user_table.setItem(row_position, 0, QTableWidgetItem(username))  # Username
            self.user_table.setItem(row_position, 1, QTableWidgetItem(user[3]))  # Role
            if user[3] == 'admin':
                # If the user is an admin, disable the remove button
                remove_button = QPushButton("Chráněno")
                remove_button.setEnabled(False)
                update_button = QPushButton("Chráněno")
                update_button.setEnabled(False)
            else:
                remove_button = QPushButton("Odebrat")
                remove_button.clicked.connect(partial(self.remove_user, user_id, username))
                update_button = QPushButton("Upravit")
                update_button.clicked.connect(partial(self.update_user, user_id, username))
                
            self.user_table.setCellWidget(row_position, 2, remove_button)
            self.user_table.setCellWidget(row_position, 3, update_button)
            # self.user_table.resizeColumnsToContents()

    def add_user(self):
        # Logic to add a new user (show a dialog to enter user details)
        pass

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
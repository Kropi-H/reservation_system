from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QTableWidget, QTableWidgetItem, QGroupBox,
                             QSpinBox, QCheckBox, QLineEdit, QFileDialog, QMessageBox,
                             QProgressBar, QTextEdit, QSplitter, QHeaderView, QWidget)
from PySide6.QtCore import Qt, QThread, Signal, QTimer
from PySide6.QtGui import QFont
from models.backup import backup_manager
from controllers.data import basic_style
import os
from datetime import datetime

class BackupWorker(QThread):
    """Worker thread pro vytváření záloh na pozadí."""
    
    progress = Signal(str)  # Zprávy o průběhu
    finished = Signal(bool, str, str)  # success, message, backup_path
    
    def __init__(self, backup_name=None):
        super().__init__()
        self.backup_name = backup_name
    
    def run(self):
        self.progress.emit("Spouštím vytváření zálohy...")
        success, message, backup_path = backup_manager.create_backup(self.backup_name)
        self.finished.emit(success, message, backup_path)

class RestoreWorker(QThread):
    """Worker thread pro obnovu databáze na pozadí."""
    
    progress = Signal(str)  # Zprávy o průběhu
    finished = Signal(bool, str)  # success, message
    
    def __init__(self, backup_path):
        super().__init__()
        self.backup_path = backup_path
    
    def run(self):
        self.progress.emit("Spouštím obnovu databáze...")
        success, message = backup_manager.restore_backup(self.backup_path)
        self.finished.emit(success, message)

class BackupDialog(QDialog):
    """Dialog pro správu záloh databáze."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Správa záloh databáze")
        self.setMinimumSize(800, 600)
        self.setStyleSheet(basic_style)
        
        self.backup_worker = None
        self.restore_worker = None
        
        self.setup_ui()
        self.load_backups()
        self.load_settings()
        
    def setup_ui(self):
        """Nastaví uživatelské rozhraní."""
        layout = QVBoxLayout(self)
        
        # Vytvoř splitter pro rozdělení na dvě části
        splitter = QSplitter(Qt.Horizontal)
        layout.addWidget(splitter)
        
        # Levá strana - Seznam záloh
        left_widget = self.create_backup_list_widget()
        splitter.addWidget(left_widget)
        
        # Pravá strana - Nastavení a akce
        right_widget = self.create_settings_widget()
        splitter.addWidget(right_widget)
        
        # Nastav poměr
        splitter.setSizes([500, 300])
        
        # Progress bar a log
        self.progress_bar = QProgressBar()
        self.progress_bar.hide()
        layout.addWidget(self.progress_bar)
        
        self.log_text = QTextEdit()
        self.log_text.setMaximumHeight(100)
        self.log_text.setFont(QFont("Consolas", 9))
        layout.addWidget(self.log_text)
        
        # Tlačítka
        button_layout = QHBoxLayout()
        self.close_button = QPushButton("Zavřít")
        self.close_button.clicked.connect(self.accept)
        button_layout.addStretch()
        button_layout.addWidget(self.close_button)
        layout.addLayout(button_layout)
    
    def create_backup_list_widget(self):
        """Vytvoří widget se seznamem záloh."""
        group = QGroupBox("Dostupné zálohy")
        layout = QVBoxLayout(group)
        
        # Tabulka se zálohami
        self.backup_table = QTableWidget()
        self.backup_table.setColumnCount(4)
        self.backup_table.setHorizontalHeaderLabels(["Název", "Velikost", "Datum vytvoření", "Akce"])
        
        # Nastav šířky sloupců
        header = self.backup_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        
        layout.addWidget(self.backup_table)
        
        # Tlačítka pro zálohy
        backup_buttons_layout = QHBoxLayout()
        
        self.create_backup_button = QPushButton("Vytvořit zálohu")
        self.create_backup_button.clicked.connect(self.create_backup)
        backup_buttons_layout.addWidget(self.create_backup_button)
        
        self.refresh_button = QPushButton("Obnovit seznam")
        self.refresh_button.clicked.connect(self.load_backups)
        backup_buttons_layout.addWidget(self.refresh_button)
        
        backup_buttons_layout.addStretch()
        layout.addLayout(backup_buttons_layout)
        
        return group
    
    def create_settings_widget(self):
        """Vytvoří widget s nastavením."""
        group = QGroupBox("Nastavení záloh")
        layout = QVBoxLayout(group)
        
        # Adresář pro zálohy
        dir_layout = QHBoxLayout()
        dir_layout.addWidget(QLabel("Adresář pro zálohy:"))
        self.backup_dir_edit = QLineEdit()
        self.backup_dir_edit.setReadOnly(True)
        dir_layout.addWidget(self.backup_dir_edit)
        
        self.browse_dir_button = QPushButton("Procházet...")
        self.browse_dir_button.clicked.connect(self.browse_backup_directory)
        dir_layout.addWidget(self.browse_dir_button)
        layout.addLayout(dir_layout)
        
        # Maximální počet záloh
        max_layout = QHBoxLayout()
        max_layout.addWidget(QLabel("Max. počet záloh:"))
        self.max_backups_spin = QSpinBox()
        self.max_backups_spin.setMinimum(1)
        self.max_backups_spin.setMaximum(100)
        max_layout.addWidget(self.max_backups_spin)
        max_layout.addStretch()
        layout.addLayout(max_layout)
        
        # Automatické zálohy
        self.auto_backup_checkbox = QCheckBox("Automatické zálohy zapnuté pro tuto instanci")
        layout.addWidget(self.auto_backup_checkbox)
        
        # Popis pro uživatele
        auto_backup_note = QLabel("💡 Tip: Pokud máte více instancí aplikace, zapněte automatické zálohy pouze u jedné z nich.")
        auto_backup_note.setWordWrap(True)
        auto_backup_note.setStyleSheet("color: #666666; font-size: 10px; padding: 5px;")
        layout.addWidget(auto_backup_note)
        
        # Frekvence automatických záloh
        freq_layout = QHBoxLayout()
        freq_layout.addWidget(QLabel("Frekvence automatických záloh (dny):"))
        self.backup_frequency_spin = QSpinBox()
        self.backup_frequency_spin.setMinimum(1)
        self.backup_frequency_spin.setMaximum(365)
        freq_layout.addWidget(self.backup_frequency_spin)
        freq_layout.addStretch()
        layout.addLayout(freq_layout)
        
        # Tlačítko pro uložení nastavení
        self.save_settings_button = QPushButton("Uložit nastavení")
        self.save_settings_button.clicked.connect(self.save_settings)
        layout.addWidget(self.save_settings_button)
        
        layout.addStretch()
        
        # Informace o databázi
        info_group = QGroupBox("Informace o databázi")
        info_layout = QVBoxLayout(info_group)
        
        self.db_info_label = QLabel()
        self.db_info_label.setWordWrap(True)
        info_layout.addWidget(self.db_info_label)
        
        layout.addWidget(info_group)
        
        # Status automatických záloh
        status_group = QGroupBox("Status automatických záloh")
        status_layout = QVBoxLayout(status_group)
        
        self.backup_status_label = QLabel()
        self.backup_status_label.setWordWrap(True)
        status_layout.addWidget(self.backup_status_label)
        
        layout.addWidget(status_group)
        
        # Přehled instancí
        instances_group = QGroupBox("Přehled všech instancí")
        instances_layout = QVBoxLayout(instances_group)
        
        self.instances_label = QLabel()
        self.instances_label.setWordWrap(True)
        self.instances_label.setFont(QFont("Consolas", 9))
        instances_layout.addWidget(self.instances_label)
        
        layout.addWidget(instances_group)
        
        return group
    
    def load_backups(self):
        """Načte seznam záloh do tabulky."""
        backups = backup_manager.get_backup_list()
        
        self.backup_table.setRowCount(len(backups))
        
        for row, (filename, filepath, size, created) in enumerate(backups):
            # Název
            self.backup_table.setItem(row, 0, QTableWidgetItem(filename))
            
            # Velikost
            size_mb = size / (1024 * 1024)
            size_text = f"{size_mb:.1f} MB" if size_mb >= 1 else f"{size / 1024:.1f} KB"
            self.backup_table.setItem(row, 1, QTableWidgetItem(size_text))
            
            # Datum
            date_text = created.strftime("%d.%m.%Y %H:%M")
            self.backup_table.setItem(row, 2, QTableWidgetItem(date_text))
            
            # Tlačítka akcí
            actions_layout = QHBoxLayout()
            
            restore_button = QPushButton("Obnovit")
            restore_button.clicked.connect(lambda checked, path=filepath: self.restore_backup(path))
            actions_layout.addWidget(restore_button)
            
            delete_button = QPushButton("Smazat")
            delete_button.clicked.connect(lambda checked, path=filepath: self.delete_backup(path))
            actions_layout.addWidget(delete_button)
            
            actions_widget = QWidget()
            actions_widget.setLayout(actions_layout)
            self.backup_table.setCellWidget(row, 3, actions_widget)
        
        self.log(f"Načteno {len(backups)} záloh")
    
    def load_settings(self):
        """Načte nastavení záloh."""
        settings = backup_manager.get_backup_settings()
        
        self.backup_dir_edit.setText(settings["backup_directory"])
        self.max_backups_spin.setValue(settings["max_backups"])
        self.auto_backup_checkbox.setChecked(settings["auto_backup_enabled"])
        self.backup_frequency_spin.setValue(settings["backup_frequency_days"])
        
        # Informace o databázi
        db_config = backup_manager.db_config
        if db_config:
            info_text = f"""Databáze: {db_config['database']}
Server: {db_config['host']}:{db_config['port']}
Uživatel: {db_config['user']}"""
            self.db_info_label.setText(info_text)
        else:
            self.db_info_label.setText("Databáze není nakonfigurována")
        
        # Status automatických záloh
        self.update_backup_status()
    
    def save_settings(self):
        """Uloží nastavení záloh."""
        settings = {
            "backup_directory": self.backup_dir_edit.text(),
            "max_backups": self.max_backups_spin.value(),
            "auto_backup_enabled": self.auto_backup_checkbox.isChecked(),
            "backup_frequency_days": self.backup_frequency_spin.value()
        }
        
        backup_manager.update_backup_settings(settings)
        self.update_backup_status()  # Aktualizuj status
        self.log("Nastavení uloženo")
        QMessageBox.information(self, "Úspěch", "Nastavení bylo úspěšně uloženo.")
    
    def browse_backup_directory(self):
        """Otevře dialog pro výběr adresáře."""
        directory = QFileDialog.getExistingDirectory(
            self, 
            "Vyberte adresář pro zálohy",
            self.backup_dir_edit.text()
        )
        if directory:
            self.backup_dir_edit.setText(directory)
    
    def create_backup(self):
        """Spustí vytváření nové zálohy."""
        if self.backup_worker and self.backup_worker.isRunning():
            QMessageBox.warning(self, "Upozornění", "Záloha již probíhá...")
            return
        
        self.create_backup_button.setEnabled(False)
        self.progress_bar.show()
        self.progress_bar.setRange(0, 0)  # Nekonečný progress
        
        self.backup_worker = BackupWorker()
        self.backup_worker.progress.connect(self.log)
        self.backup_worker.finished.connect(self.backup_finished)
        self.backup_worker.start()
    
    def backup_finished(self, success, message, backup_path):
        """Callback po dokončení zálohy."""
        self.create_backup_button.setEnabled(True)
        self.progress_bar.hide()
        
        if success:
            self.log(f"✅ {message}")
            self.load_backups()  # Obnovit seznam
            QMessageBox.information(self, "Úspěch", message)
        else:
            self.log(f"❌ {message}")
            QMessageBox.critical(self, "Chyba", message)
    
    def restore_backup(self, backup_path):
        """Spustí obnovu ze zálohy."""
        if self.restore_worker and self.restore_worker.isRunning():
            QMessageBox.warning(self, "Upozornění", "Obnova již probíhá...")
            return
        
        # Potvrzovací dialog
        reply = QMessageBox.question(
            self, 
            "Potvrzení obnovy",
            f"Opravdu chcete obnovit databázi ze zálohy?\n\n"
            f"VAROVÁNÍ: Všechna aktuální data budou přepsána!\n\n"
            f"Záloha: {os.path.basename(backup_path)}",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply != QMessageBox.Yes:
            return
        
        self.progress_bar.show()
        self.progress_bar.setRange(0, 0)
        
        self.restore_worker = RestoreWorker(backup_path)
        self.restore_worker.progress.connect(self.log)
        self.restore_worker.finished.connect(self.restore_finished)
        self.restore_worker.start()
    
    def restore_finished(self, success, message):
        """Callback po dokončení obnovy."""
        self.progress_bar.hide()
        
        if success:
            self.log(f"✅ {message}")
            QMessageBox.information(self, "Úspěch", f"{message}\n\nDoporučujeme restartovat aplikaci.")
        else:
            self.log(f"❌ {message}")
            QMessageBox.critical(self, "Chyba", message)
    
    def delete_backup(self, backup_path):
        """Smaže zálohu."""
        filename = os.path.basename(backup_path)
        
        reply = QMessageBox.question(
            self,
            "Smazání zálohy",
            f"Opravdu chcete smazat zálohu?\n\n{filename}",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            success, message = backup_manager.delete_backup(backup_path)
            
            if success:
                self.log(f"🗑️ {message}")
                self.load_backups()  # Obnovit seznam
            else:
                self.log(f"❌ {message}")
                QMessageBox.critical(self, "Chyba", message)
    
    def update_backup_status(self):
        """Aktualizuje status automatických záloh a přehled instancí."""
        from models.settings import get_settings
        should_backup = backup_manager.should_create_auto_backup()
        last_backup_date = get_settings("last_backup_date")
        
        # Status této instance
        instance_info = backup_manager.get_instance_info()
        status_text = f"""Tato instance ({instance_info['hostname']} #{instance_info['hash']}):
Automatické zálohy: {'🟢 Zapnuté' if backup_manager.auto_backup_enabled else '🔴 Vypnuté'}
Frekvence: každých {backup_manager.backup_frequency_days} dní
Poslední záloha: {last_backup_date if last_backup_date else 'Žádná'}  
Další záloha potřeba: {'🟡 Ano' if should_backup else '🟢 Ne'}"""
        
        self.backup_status_label.setText(status_text)
        
        # Přehled všech instancí
        all_instances = backup_manager.get_all_instances_info()
        if all_instances:
            instances_text = "Registrované instance:\n"
            for inst in all_instances:
                current_marker = "👈 TATO" if inst['is_current'] else ""
                status_icon = "🟢" if inst['auto_backup_enabled'] else "🔴"
                instances_text += f"{status_icon} {inst['hostname']} (#{inst['hash']}) {current_marker}\n"
        else:
            instances_text = "Žádné registrované instance"
            
        self.instances_label.setText(instances_text)
    
    def log(self, message):
        """Přidá zprávu do logu."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.append(f"[{timestamp}] {message}")
        # Automaticky skrolovat dolů
        scrollbar = self.log_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
    def closeEvent(self, event):
        """Přepíše zavření okna."""
        # Zastav všechny běžící worker threads
        if self.backup_worker and self.backup_worker.isRunning():
            self.backup_worker.terminate()
            self.backup_worker.wait()
        
        if self.restore_worker and self.restore_worker.isRunning():
            self.restore_worker.terminate() 
            self.restore_worker.wait()
        
        event.accept()
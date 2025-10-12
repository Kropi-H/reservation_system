from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QSpinBox, QSlider, QDialogButtonBox, QMessageBox
from PySide6.QtCore import Qt
from models.settings import get_settings, save_settings
from models.rezervace import smaz_rezervace_starsi_nez
from models.backup import BackupManager
from controllers.data import basic_style

class SmazRezervaceDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Zrušení rezervací a ordinačních časů")
        self.setFixedSize(350, 300)

        # Kontrola, zda má tato instance povoleno zálohování
        backup_manager = BackupManager()
        self.has_backup_permission = backup_manager.auto_backup_enabled
        self.instance_id = backup_manager.instance_id

        self.days_to_keep = int(get_settings("days_to_keep"))

        # Jednoduché stylování
        self.setStyleSheet(basic_style)

        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(15, 15, 15, 15)

        # Informace o oprávnění
        permission_label = QLabel()
        if self.has_backup_permission:
            permission_label.setText(f"✅ Instance: {self.instance_id}\nTato instance má povoleno spravovat zálohy a mazat stará data.")
            permission_label.setStyleSheet("color: green; font-weight: bold; background-color: #e8f5e8; padding: 8px; border-radius: 4px;")
        else:
            permission_label.setText(f"❌ Instance: {self.instance_id}\nTato instance NEMÁ povoleno mazat stará data.\nPovolte zálohy v menu Databáze → Zálohy, pokud chcete mazat data.")
            permission_label.setStyleSheet("color: red; font-weight: bold; background-color: #ffeaea; padding: 8px; border-radius: 4px;")
        
        permission_label.setAlignment(Qt.AlignCenter)
        permission_label.setWordWrap(True)
        layout.addWidget(permission_label)

        # Hlavní label
        if self.has_backup_permission:
            self.label = QLabel(f"Zadejte počet dní pro smazání rezervací a ordinačních časů:\nPokud je 0, data se mazat nebudou.\nAktuální nastavení: {self.days_to_keep} dní.")
        else:
            self.label = QLabel(f"Mazání dat je zakázáno pro tuto instanci.\nAktuální nastavení: {self.days_to_keep} dní.")
        
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setWordWrap(True)
        layout.addWidget(self.label)

        # SpinBox
        spinbox_layout = QHBoxLayout()
        spinbox_label = QLabel("Počet dní:")
        
        self.days_input = QSpinBox()
        self.days_input.setMinimum(0)
        self.days_input.setMaximum(365)
        self.days_input.setValue(self.days_to_keep)
        self.days_input.setSuffix(" dní")
        self.days_input.setEnabled(self.has_backup_permission)  # Zakázáno pokud nemá oprávnění
        
        spinbox_layout.addWidget(spinbox_label)
        spinbox_layout.addWidget(self.days_input)
        layout.addLayout(spinbox_layout)

        # Slider
        self.days_slider = QSlider(Qt.Horizontal)
        self.days_slider.setMinimum(0)
        self.days_slider.setMaximum(365)
        self.days_slider.setValue(self.days_to_keep)
        self.days_slider.setEnabled(self.has_backup_permission)  # Zakázáno pokud nemá oprávnění
        layout.addWidget(self.days_slider)

        # Tlačítka
        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        if self.has_backup_permission:
            self.button_box.button(QDialogButtonBox.Ok).setText("Potvrdit")
        else:
            self.button_box.button(QDialogButtonBox.Ok).setText("Není povoleno")
            self.button_box.button(QDialogButtonBox.Ok).setEnabled(False)
        self.button_box.button(QDialogButtonBox.Cancel).setText("Zrušit")
        layout.addWidget(self.button_box)

        # Propojení signálů
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        
        # Synchronizace mezi spinboxem a sliderem
        self.days_input.valueChanged.connect(self.days_slider.setValue)
        self.days_slider.valueChanged.connect(self.days_input.setValue)

    def get_days(self):
        """Vrátí počet dní pro uchování rezervací."""
        return self.days_input.value()
    
    def set_days_to_keep(self):
        """Nastaví počet dní pro uchování rezervací a ordinačních časů."""
        # Kontrola oprávnění
        if not self.has_backup_permission:
            QMessageBox.warning(
                self,
                "Zakázáno",
                f"Tato instance ({self.instance_id}) nemá povoleno mazat stará data.\n\n"
                "Pouze instance s povoleným automatickým zálohováním mohou mazat stará data.\n"
                "Povolte zálohy v menu Databáze → Zálohy."
            )
            return None
            
        try:
            days = self.days_input.value()
            if days <= 0:
                raise ValueError("Data se nebudou mazat, protože počet dní je 0.")
            
            self.days_input.setValue(days)
            self.days_slider.setValue(days)
            save_settings({"days_to_keep": str(days)})
            result = smaz_rezervace_starsi_nez(days)
            
            # Zobraz informaci o výsledku mazání
            if result and isinstance(result, dict):
                zprava = (f"Úspěšně smazáno:\n"
                         f"• {result.get('pocet_smazanych_rezervaci', 0)} rezervací\n"
                         f"• {result.get('pocet_smazanych_ordinacnich_casu', 0)} ordinačních časů\n"
                         f"Starších než {result.get('datum_hranice', 'neznámé datum')}\n\n"
                         f"Instance: {self.instance_id}")
                QMessageBox.information(self, "Výsledek mazání", zprava)
            
            return result
        except ValueError as e:
             QMessageBox.information(
                      self,
                      "Zpráva:",
                      f"{e}"
                  )
             return None
            
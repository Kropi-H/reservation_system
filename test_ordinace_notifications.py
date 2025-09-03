#!/usr/bin/env python3
"""
Test skript pro ověření real-time notifikací ordinací a doktorů
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models.ordinace import add_ordinace, update_ordinace_db, remove_ordinace
from models.doktori import add_doctor, update_doctor, deactivate_doctor, remove_doctor
from models.database_listener import DatabaseListener
from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import QApplication
import time

class TestListener(QObject):
    def __init__(self):
        super().__init__()
        self.received_notifications = []
    
    def on_ordinace_changed(self, data):
        print(f"🏥 TEST: Ordinace změna - {data}")
        self.received_notifications.append(('ordinace', data))
    
    def on_doctor_changed(self, data):
        print(f"👨‍⚕️ TEST: Doktor změna - {data}")
        self.received_notifications.append(('doctor', data))

def test_notifications():
    """Test real-time notifikací pro ordinace a doktory."""
    print("🧪 Spouštím test real-time notifikací...")
    
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    
    # Nastav test listener
    test_listener = TestListener()
    
    try:
        # Nastav database listener
        db_listener = DatabaseListener()
        db_listener.ordinace_changed.connect(test_listener.on_ordinace_changed)
        db_listener.doctor_changed.connect(test_listener.on_doctor_changed)
        db_listener.start_listening(['ordinace_changes', 'doctor_changes'])
        
        time.sleep(1)  # Krátká pauza pro inicializaci
        
        print("\n📋 Testování ordinací...")
        
        # Test 1: Přidání ordinace
        print("1️⃣ Přidávám testovací ordinaci...")
        ordinace_data = {
            'nazev': 'Test Ordinace',
            'patro': '1',
            'popis': 'Testovací ordinace pro notifikace'
        }
        add_ordinace(ordinace_data)
        time.sleep(0.5)
        
        # Test 2: Úprava ordinace (nejdříve najdeme ID)
        from models.ordinace import get_all_ordinace
        ordinace_list = get_all_ordinace()
        test_ordinace = None
        for ord in ordinace_list:
            if isinstance(ord, dict) and ord['nazev'] == 'Test Ordinace':
                test_ordinace = ord
                break
        
        if test_ordinace:
            print("2️⃣ Upravuji testovací ordinaci...")
            update_data = {
                'nazev': 'Test Ordinace Upraveno',
                'patro': '2',
                'popis': 'Upravená testovací ordinace'
            }
            update_ordinace_db(test_ordinace['ordinace_id'], update_data)
            time.sleep(0.5)
            
            print("3️⃣ Odstraňuji testovací ordinaci...")
            remove_ordinace(test_ordinace['ordinace_id'], 'Test Ordinace Upraveno')
            time.sleep(0.5)
        
        print("\n👨‍⚕️ Testování doktorů...")
        
        # Test 3: Přidání doktora
        print("4️⃣ Přidávám testovacího doktora...")
        doctor_data = {
            'jmeno': 'Test',
            'prijmeni': 'Doktor',
            'specializace': 'Testování',
            'isActive': True,
            'color': '#FF0000'
        }
        add_doctor(doctor_data)
        time.sleep(0.5)
        
        # Test 4: Najít a upravit doktora
        from models.doktori import get_all_doctors
        doctors_list = get_all_doctors()
        test_doctor = None
        for doc in doctors_list:
            if doc[1] == 'Test' and doc[2] == 'Doktor':  # jmeno, prijmeni
                test_doctor = doc
                break
        
        if test_doctor:
            doctor_id = test_doctor[0]  # doktor_id je první sloupec
            
            print("5️⃣ Upravuji testovacího doktora...")
            update_data = {
                'jmeno': 'Test Upraveny',
                'prijmeni': 'Doktor',
                'specializace': 'Upravené testování',
                'isActive': True,
                'color': '#00FF00'
            }
            update_doctor(update_data, doctor_id)
            time.sleep(0.5)
            
            print("6️⃣ Deaktivuji testovacího doktora...")
            deactivate_doctor(doctor_id)
            time.sleep(0.5)
            
            print("7️⃣ Odstraňuji testovacího doktora...")
            remove_doctor(doctor_id)
            time.sleep(0.5)
        
        time.sleep(1)  # Pauza pro zpracování všech notifikací
        
        # Zastavit listener
        db_listener.stop_listening()
        
        print(f"\n✅ Test dokončen! Přijato {len(test_listener.received_notifications)} notifikací:")
        for i, (typ, data) in enumerate(test_listener.received_notifications, 1):
            operation = data.get('operation', 'N/A')
            print(f"   {i}. {typ.upper()}: {operation}")
        
        if len(test_listener.received_notifications) >= 6:  # Očekáváme 3 ordinace + 4 doktor notifikace
            print("🎉 Test ÚSPĚŠNÝ - všechny notifikace byly přijaty!")
        else:
            print("⚠️ Test ČÁSTEČNĚ ÚSPĚŠNÝ - některé notifikace nebyly přijaty")
            
    except Exception as e:
        print(f"❌ Chyba během testu: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_notifications()

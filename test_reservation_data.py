#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Test načítání dat pro úpravu rezervace
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models.rezervace import ziskej_rezervace_dne
from datetime import datetime

def test_reservation_data_structure():
    """Test struktury dat rezervace pro editaci"""
    print("=== Test struktury dat rezervace ===")
    
    try:
        # Získáme rezervace pro dnešek
        today = datetime.now().strftime("%Y-%m-%d")
        rezervace = ziskej_rezervace_dne(today)
        
        if not rezervace:
            print("❌ Žádné rezervace pro dnešek")
            
            # Zkusíme jiný den - např. včera nebo zítra
            yesterday = datetime.now().strftime("%Y-%m-%d")
            rezervace = ziskej_rezervace_dne("2025-08-23")  # Pevné datum
            
        if rezervace:
            print(f"✅ Nalezeno {len(rezervace)} rezervací")
            
            for i, r in enumerate(rezervace):
                print(f"\n--- Rezervace {i+1} ---")
                print(f"Struktura dat: {len(r)} položek")
                print(f"[0] Termín: {r[0]} (type: {type(r[0])})")
                print(f"[1] ID: {r[1]}")
                print(f"[2] Doktor: {r[2]}")
                print(f"[3] Barva: {r[3]}")
                print(f"[4] Pacient: {r[4]}")
                print(f"[5] Majitel: {r[5]}")
                print(f"[6] Kontakt: {r[6]}")
                print(f"[7] Druh: {r[7]}")
                print(f"[8] Ordinace: {r[8]}")
                print(f"[9] Poznámka: {r[9]}")
                print(f"[10] Cas_od: {r[10]}")
                print(f"[11] Cas_do: {r[11]}")
                
                # Simulace vytvoření FormularRezervace
                print(f"\n🔍 Simulace editace rezervace {r[1]}:")
                print(f"   rezervace_data = {r}")
                break
        else:
            print("❌ Žádné rezervace nalezeny")
            
    except Exception as e:
        print(f"❌ Chyba při testu dat rezervace: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_reservation_data_structure()

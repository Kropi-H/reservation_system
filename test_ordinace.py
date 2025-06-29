#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models.ordinace import get_all_ordinace

def get_ordinace_list():
    ordinace = get_all_ordinace()
    # Vytvoř seznam unikátních názvů ordinací
    nazvy = []
    for i in ordinace:
        nazev = f"{i[1]}"
        if nazev not in nazvy:
            nazvy.append(nazev)
    return nazvy

print("=== TEST ORDINACÍ ===")
try:
    ordinace_raw = get_all_ordinace()
    print(f"Všechny ordinace z databáze: {len(ordinace_raw)}")
    for ord in ordinace_raw:
        print(f"  {ord}")
    
    ordinace_list = get_ordinace_list()
    print(f"Unikátní názvy: {ordinace_list}")
    print(f"Počet unikátních: {len(ordinace_list)}")
    
except Exception as e:
    print(f"Chyba: {e}")
    import traceback
    traceback.print_exc()

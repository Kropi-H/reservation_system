#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Debug načítání rezervací
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models.databaze import get_connection
from datetime import datetime

def debug_reservations():
    """Debug načítání rezervací"""
    print("=== Debug načítání rezervací ===")
    
    try:
        with get_connection() as conn:
            cur = conn.cursor()
            
            # Zobrazíme všechny rezervace
            cur.execute("SELECT * FROM Rezervace")
            all_reservations = cur.fetchall()
            print(f"✅ Celkem rezervací v DB: {len(all_reservations)}")
            
            for res in all_reservations:
                print(f"   {res}")
            
            # Zkusíme dnešní datum
            today = datetime.now().strftime("%Y-%m-%d")
            print(f"\n🔍 Hledáme rezervace pro: {today}")
            
            cur.execute("SELECT termin FROM Rezervace")
            dates = cur.fetchall()
            print(f"✅ Termíny v DB:")
            for date in dates:
                print(f"   {date[0]} (type: {type(date[0])})")
            
            # Zkusíme jiný formát
            cur.execute("SELECT * FROM Rezervace WHERE DATE(termin) = %s", (today,))
            today_reservations = cur.fetchall()
            print(f"\n✅ Rezervace pro {today}: {len(today_reservations)}")
            
            if not today_reservations:
                # Zkusíme bez time komponenty
                cur.execute("SELECT * FROM Rezervace WHERE termin::date = %s", (today,))
                today_reservations2 = cur.fetchall()
                print(f"✅ Rezervace s ::date: {len(today_reservations2)}")
            
    except Exception as e:
        print(f"❌ Chyba při debug: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_reservations()

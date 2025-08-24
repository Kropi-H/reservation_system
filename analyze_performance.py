#!/usr/bin/env python3
import time
from datetime import datetime
from models.rezervace import ziskej_rezervace_dne
from models.doktori import ziskej_rozvrh_doktoru_dne
from views.hlavni_okno import get_ordinace_list

def measure_time(func, *args, **kwargs):
    start = time.time()
    result = func(*args, **kwargs)
    end = time.time()
    return result, end - start

def analyze_performance():
    datum = datetime.now().strftime("%Y-%m-%d")
    print(f"Analýza výkonu pro datum: {datum}")
    print("=" * 50)
    
    # Test jednotlivých dotazů
    print("1. Testování ziskej_rezervace_dne()...")
    rezervace, time1 = measure_time(ziskej_rezervace_dne, datum)
    print(f"   Počet rezervací: {len(rezervace)}")
    print(f"   Čas: {time1:.3f} sekund")
    
    print("\n2. Testování ziskej_rozvrh_doktoru_dne()...")
    rozvrh, time2 = measure_time(ziskej_rozvrh_doktoru_dne, datum)
    print(f"   Počet záznamů rozvrhu: {len(rozvrh)}")
    print(f"   Čas: {time2:.3f} sekund")
    
    print("\n3. Testování get_ordinace_list()...")
    ordinace, time3 = measure_time(get_ordinace_list)
    print(f"   Počet ordinací: {len(ordinace)}")
    print(f"   Čas: {time3:.3f} sekund")
    
    total_time = time1 + time2 + time3
    print("\n" + "=" * 50)
    print(f"CELKOVÝ ČAS: {total_time:.3f} sekund")
    
    if total_time > 1.0:
        print("⚠️ POMALÉ NAČÍTÁNÍ! Doporučení:")
        if time1 > 0.5:
            print("  - Optimalizovat dotaz na rezervace")
        if time2 > 0.5:
            print("  - Optimalizovat dotaz na rozvrh doktorů")
        if time3 > 0.5:
            print("  - Optimalizovat dotaz na ordinace")
    else:
        print("✅ Výkon je v pořádku")

if __name__ == "__main__":
    try:
        analyze_performance()
    except Exception as e:
        print(f"Chyba při analýze: {e}")
        import traceback
        traceback.print_exc()

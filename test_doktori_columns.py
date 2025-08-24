#!/usr/bin/env python3
from models.databaze import get_doktori

try:
    doktori = get_doktori()
    if doktori:
        print("Počet doktorů:", len(doktori))
        print("Typ prvního záznamu:", type(doktori[0]))
        print("Klíče/sloupce:")
        if isinstance(doktori[0], dict):
            for key in doktori[0].keys():
                print(f"  - {key}: {doktori[0][key]}")
        else:
            print("  Tuple format:", doktori[0])
    else:
        print("Žádní doktoři nenalezeni")
except Exception as e:
    print(f"Chyba: {e}")
    import traceback
    traceback.print_exc()

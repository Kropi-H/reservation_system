#!/usr/bin/env python3
from models.rezervace import ziskej_rezervace_dne
from datetime import datetime

try:
    datum = datetime.now().strftime("%Y-%m-%d")
    rezervace = ziskej_rezervace_dne(datum)
    print(f"Počet rezervací: {len(rezervace)}")
    if rezervace:
        print("První rezervace:")
        for i, val in enumerate(rezervace[0]):
            print(f"  [{i}]: {repr(val)} (type: {type(val)})")
    else:
        print("Žádné rezervace pro dnešní den")
except Exception as e:
    print(f"Chyba: {e}")
    import traceback
    traceback.print_exc()

#!/usr/bin/env python3
# Test script pro debug načítání rezervací

from models.rezervace import ziskej_rezervace_dne
from datetime import datetime

# Získej dnešní datum
dnes = datetime.now().strftime('%Y-%m-%d')
print(f"Testuji rezervace pro datum: {dnes}")

# Načti rezervace
rezervace = ziskej_rezervace_dne(dnes)

print(f"Nalezeno {len(rezervace)} rezervací")
print()

for i, rez in enumerate(rezervace):
    print(f"=== Rezervace {i+1} ===")
    print(f"Délka tuple: {len(rez)}")
    for j, hodnota in enumerate(rez):
        print(f"  Index {j}: {repr(hodnota)} (typ: {type(hodnota).__name__})")
    print()
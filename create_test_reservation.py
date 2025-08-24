#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Vytvoření testovací rezervace
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models.rezervace import pridej_rezervaci
from datetime import datetime

def create_test_reservation():
    """Vytvoří testovací rezervaci"""
    print("=== Vytvoření testovací rezervace ===")
    
    try:
        # Vytvoříme rezervaci na dnes
        today = datetime.now().strftime("%Y-%m-%d")
        
        result = pridej_rezervaci(
            pacient_jmeno="Test Pes",
            pacient_druh="Pes",
            majitel_pacienta="Test Majitel",
            majitel_kontakt="123456789",
            doktor="Dr. Test",
            note="Test poznámka pro editaci",
            termin=today,
            cas_od="09:00",
            cas_do="10:00",
            mistnost="Ordinace 1"
        )
        
        print(f"✅ Testovací rezervace vytvořena s ID: {result}")
        
        # Vytvoříme ještě jednu rezervaci
        result2 = pridej_rezervaci(
            pacient_jmeno="Test Kočka",
            pacient_druh="Kočka",
            majitel_pacienta="Test Majitel 2",
            majitel_kontakt="987654321",
            doktor="Dr. Druhý",
            note="Druhá test poznámka",
            termin=today,
            cas_od="11:00", 
            cas_do="12:00",
            mistnost="Ordinace 2"
        )
        
        print(f"✅ Druhá testovací rezervace vytvořena s ID: {result2}")
        
    except Exception as e:
        print(f"❌ Chyba při vytváření testovací rezervace: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    create_test_reservation()

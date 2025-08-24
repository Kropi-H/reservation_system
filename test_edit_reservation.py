#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Test úpravy rezervace
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models.databaze import get_connection
from models.rezervace import aktualizuj_rezervaci

def test_edit_reservation():
    """Test úpravy rezervace"""
    print("=== Test úpravy rezervace ===")
    
    # Nejdříve získáme nějakou existující rezervaci
    try:
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM Rezervace LIMIT 1")
            rezervace = cur.fetchone()
            
            if not rezervace:
                print("❌ Žádné rezervace v databázi pro test")
                return
                
            print(f"✅ Nalezena rezervace: {rezervace}")
            rezervace_id = rezervace[0]  # prvním sloupcem by mělo být ID
            
            # Pokusíme se rezervaci aktualizovat
            result = aktualizuj_rezervaci(
                rezervace_id=rezervace_id,
                pacient_jmeno="Test Pacient UPDATED",
                pacient_druh="Pes",
                majitel_pacienta="Test Majitel",
                majitel_kontakt="123456789",
                doktor="Dr. Test",
                note="Test poznámka",
                termin="2025-08-25",
                cas_od="09:00",
                cas_do="10:00",
                mistnost="Ordinace 1"
            )
            
            print(f"✅ Výsledek aktualizace: {result}")
            
            # Ověříme změnu
            cur.execute("SELECT * FROM Rezervace WHERE rezervace_id = %s", (rezervace_id,))
            updated_rezervace = cur.fetchone()
            print(f"✅ Aktualizovaná rezervace: {updated_rezervace}")
            
    except Exception as e:
        print(f"❌ Chyba při testu úpravy rezervace: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_edit_reservation()

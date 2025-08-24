#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Test controlleru úpravy rezervace
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from controllers.rezervace_controller import aktualizuj_rezervaci
from models.databaze import get_connection

def test_controller_edit():
    """Test controlleru pro úpravu rezervace"""
    print("=== Test controlleru úpravy rezervace ===")
    
    # Získáme existující rezervaci
    try:
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT rezervace_id FROM Rezervace LIMIT 1")
            row = cur.fetchone()
            
            if not row:
                print("❌ Žádné rezervace pro test")
                return
                
            rezervace_id = row[0]
            print(f"✅ Testuji s rezervací ID: {rezervace_id}")
            
            # Test controlleru
            result = aktualizuj_rezervaci(
                rezervace_id=rezervace_id,
                pacient_jmeno="Controller Test Pet",
                pacient_druh="Králík",
                majitel_pacienta="Controller Test Owner",
                majitel_kontakt="555123456",
                doktor="Dr. Controller",
                note="Controller test note",
                termin="2025-08-25",
                cas_od="11:00",
                cas_do="12:00",
                mistnost="Ordinace 2"
            )
            
            print(f"✅ Výsledek z controlleru: {result}")
            
            if result:
                print("🎉 Controller úprava rezervace funguje!")
            else:
                print("❌ Controller úprava rezervace nefunguje!")
            
    except Exception as e:
        print(f"❌ Chyba při testu controlleru: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_controller_edit()

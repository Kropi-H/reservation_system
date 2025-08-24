#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Test detailní úpravy rezervace
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models.databaze import get_connection

def test_reservation_details():
    """Test detailů rezervace a souvisejících tabulek"""
    print("=== Test detailů rezervace ===")
    
    try:
        with get_connection() as conn:
            cur = conn.cursor()
            
            # Získáme celý detail rezervace s JOIN
            cur.execute("""
                SELECT 
                    r.rezervace_id,
                    r.pacient_id,
                    r.doktor_id, 
                    r.ordinace_id,
                    r.termin,
                    r.cas_od,
                    r.cas_do,
                    p.jmeno_zvirete,
                    p.druh,
                    p.majitel_jmeno,
                    p.majitel_telefon,
                    p.poznamka,
                    d.jmeno as doktor_jmeno,
                    d.prijmeni as doktor_prijmeni,
                    o.nazev as ordinace_nazev
                FROM Rezervace r
                LEFT JOIN Pacienti p ON r.pacient_id = p.pacient_id
                LEFT JOIN Doktori d ON r.doktor_id = d.doktor_id  
                LEFT JOIN Ordinace o ON r.ordinace_id = o.ordinace_id
                LIMIT 1
            """)
            
            rezervace = cur.fetchone()
            if rezervace:
                print("✅ Detail rezervace:")
                print(f"   ID: {rezervace[0]}")
                print(f"   Pacient: {rezervace[7]} ({rezervace[8]})")
                print(f"   Majitel: {rezervace[9]}, tel: {rezervace[10]}")
                print(f"   Poznámka: {rezervace[11]}")
                print(f"   Doktor: {rezervace[12]} {rezervace[13]}")
                print(f"   Ordinace: {rezervace[14]}")
                print(f"   Termín: {rezervace[4]}, {rezervace[5]}-{rezervace[6]}")
            
            # Test aktualizace pacienta
            print("\n=== Test aktualizace pacienta ===")
            cur.execute("""
                UPDATE Pacienti 
                SET jmeno_zvirete = %s, druh = %s, majitel_jmeno = %s, majitel_telefon = %s, poznamka = %s
                WHERE pacient_id = %s
            """, ("UPDATED PET", "Kočka", "UPDATED OWNER", "999888777", "UPDATED NOTE", rezervace[1]))
            
            print(f"✅ Počet upravených řádků pacienta: {cur.rowcount}")
            
            # Ověříme změnu
            cur.execute("SELECT * FROM Pacienti WHERE pacient_id = %s", (rezervace[1],))
            updated_pacient = cur.fetchone()
            print(f"✅ Aktualizovaný pacient: {updated_pacient}")
            
    except Exception as e:
        print(f"❌ Chyba při testu detailů rezervace: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_reservation_details()

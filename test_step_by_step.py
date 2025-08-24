#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Detailní test vytvoření rezervace krok za krokem
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models.databaze import get_connection, get_or_create
from datetime import datetime

def test_step_by_step_reservation():
    """Test vytvoření rezervace krok za krokem"""
    print("=== Test vytvoření rezervace krok za krokem ===")
    
    try:
        with get_connection() as conn:
            cur = conn.cursor()
            
            print("1. Vytváříme doktora...")
            doc_id = get_or_create(
                cur,
                table="Doktori",
                unique_cols=("jmeno","prijmeni"),
                data_cols={
                    "jmeno": "Test",
                    "prijmeni": "Doktor",
                    "isActive": 1,
                    "specializace": "Test",
                    "color": "#FF0000"
                }
            )
            print(f"✅ Doktor ID: {doc_id}")
            
            print("2. Vytváříme pacienta...")
            pac_id = get_or_create(
                cur,
                table="Pacienti",
                unique_cols=("jmeno_zvirete", "majitel_jmeno"),
                data_cols={
                    "jmeno_zvirete": "Test Pet",
                    "druh": "Pes",
                    "majitel_jmeno": "Test Owner",
                    "majitel_telefon": "123456789",
                    "poznamka": "Test note"
                }
            )
            print(f"✅ Pacient ID: {pac_id}")
            
            print("3. Vytváříme ordinaci...")
            ord_id = get_or_create(
                cur,
                table="Ordinace",
                unique_cols=("nazev",),
                data_cols={"nazev": "Test Ordinace"}
            )
            print(f"✅ Ordinace ID: {ord_id}")
            
            print("4. Vytváříme rezervaci...")
            termin = "2025-08-23"
            cas_od = "10:00"
            cas_do = "11:00"
            
            cur.execute(
                """
                INSERT INTO Rezervace
                (pacient_id, doktor_id, ordinace_id, termin, cas_od, cas_do)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING rezervace_id
                """,
                (pac_id, doc_id, ord_id, termin, cas_od, cas_do)
            )
            
            result = cur.fetchone()
            rezervace_id = result[0] if result else None
            print(f"✅ Rezervace ID: {rezervace_id}")
            
            # Ověříme, že se rezervace skutečně vytvořila
            cur.execute("SELECT COUNT(*) FROM Rezervace")
            count = cur.fetchone()[0]
            print(f"✅ Celkem rezervací v DB: {count}")
            
            # Explicitní commit
            conn.commit()
            print("✅ Změny commitnuty")
            
    except Exception as e:
        print(f"❌ Chyba při testu krok za krokem: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_step_by_step_reservation()

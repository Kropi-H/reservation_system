from models import rezervace

def uloz_rezervaci(pacient_jmeno, pacient_druh, majitel_pacienta, majitel_kontakt, doktor, note, cas, mistnost):
    try:
        rezervace.pridej_rezervaci(pacient_jmeno, pacient_druh, majitel_pacienta, majitel_kontakt, doktor, note, cas, mistnost)
        #print(f"Ukládám rezervaci: {pacient_jmeno}, {pacient_druh}, {majitel_pacienta}, {majitel_kontakt}, {doktor}, {note}, {cas}, {mistnost}")
        # Zde by měl být kód pro uložení rezervace do databáze
        return True
    except Exception as e:
        print(f"Chyba: {e}")
        return False
      
def aktualizuj_rezervaci(rezervace_id, pacient_jmeno, pacient_druh, majitel_pacienta, majitel_kontakt, doktor, note, cas, mistnost):
    try:
        rezervace.aktualizuj_rezervaci(rezervace_id, pacient_jmeno, pacient_druh, majitel_pacienta, majitel_kontakt, doktor, note, cas, mistnost)
        #print(f"Aktualizuji rezervaci: {rezervace_id}, {pacient_jmeno}, {pacient_druh}, {majitel_pacienta}, {majitel_kontakt}, {doktor}, {note}, {cas}, {mistnost}")
        # Zde by měl být kód pro aktualizaci rezervace v databázi
        return True
    except Exception as e:
        print(f"Chyba: {e}")
        return False
      
def odstran_rezervaci_z_db(rezervace_id):
    try:
        rezervace.odstran_rezervaci(rezervace_id)
        #print(f"Odstraňuji rezervaci: {rezervace_id}")
        # Zde by měl být kód pro odstranění rezervace z databáze
        return True
    except Exception as e:
        print(f"Chyba: {e}")
        return False
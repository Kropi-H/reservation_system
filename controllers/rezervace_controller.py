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
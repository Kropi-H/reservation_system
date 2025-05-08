from models import rezervace

def uloz_rezervaci(pacient, doktor, cas, mistnost):
    try:
        rezervace.pridej_rezervaci(pacient, doktor, cas, mistnost)
        return True
    except Exception as e:
        print(f"Chyba: {e}")
        return False
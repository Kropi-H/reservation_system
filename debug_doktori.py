from models.databaze import get_doktori

doktori = get_doktori()
print("Všichni doktoři:")
for doktor in doktori:
    full_name = ' '.join(f"{doktor['jmeno']} {doktor['prijmeni']}".split())
    print(f"'{full_name}' - ID:{doktor['doktor_id']} Active:{doktor['isactive']} Color:{doktor['color']}")
    if doktor['jmeno'].strip() in ['Pavla', 'Zuzana']:
        print(f"  *** PROBLEMATICKÝ DOKTOR ***")
        print(f"  Raw jméno: '{doktor['jmeno']}'")
        print(f"  Raw příjmení: '{doktor['prijmeni']}'")

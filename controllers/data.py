doktori = [
  {
  'id': 1,
  'jmeno': 'Aleš',
  'prijmeni': 'Novák',
  'specializace': 'Chirurgie'
},{
  'id': 2,
  'jmeno': 'Eva',
  'prijmeni': 'Svobodová',
  'specializace': 'Interna'
},
{  'id': 3,
  'jmeno': 'Petr',
  'prijmeni': 'Černý',
  'specializace': 'Dermatologie'
}
]

ordinace = [
  {
  'id': 1,
  'nazev': 'Ordinace 1',
  'patro': 1,
  'popis': 'Ordinace pro psy a kočky'
},{
  'id': 2,
  'nazev': 'Ordinace 2',
  'patro': 1,
  'popis': 'Ordinace pro exotická zvířata'
},
{  'id': 3,
  'nazev': 'Ordinace 3',
  'patro': 2,
  'popis': 'Ordinace pro chirurgické zákroky'
}
]

pacienti = [
  {
  'id': 1,
  'jmeno_zvirete': 'Rex',
  'druh': 'Pes',
  'majitel_jmeno': 'Jan Novák',
  'majitel_telefon': '+420123456789'
},{
  'id': 2,
  'jmeno_zvirete': 'Mia',
  'druh': 'Kočka',
  'majitel_jmeno': 'Petra Svobodová',
  'majitel_telefon': '+420987654321'
},
{  'id': 3,
  'jmeno_zvirete': 'Kiki',
  'druh': 'Papoušek',
  'majitel_jmeno': 'Petr Černý',
  'majitel_telefon': '+420555555555'
}
]

rezervace = [
  {
  'id': 1,
  'pacient_id': 1,
  'doktor_id': 1,
  'ordinace_id': 1,
  'termin': '2025-05-06 13:30:00',
  'poznamka': 'Kontrola'
},{
  'id': 2,
  'pacient_id': 2,
  'doktor_id': 2,
  'ordinace_id': 2,
  'termin': '2025-05-06 14:00:00',
  'poznamka': 'Očkování'
},
{  'id': 3,
  'pacient_id': 3,
  'doktor_id': 3,
  'ordinace_id': 3,
  'termin': '2025-05-06 15:00:00',
  'poznamka': 'Operace'
}
]
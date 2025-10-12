"""
Modul pro tisk denních rezervací veterinární ordinace.
Vytváří HTML výstup s barevnými kolečky doktorů podle rozvrhu.
"""

from datetime import datetime, timedelta
from PySide6.QtWidgets import QMessageBox
from PySide6.QtPrintSupport import QPrinter, QPrintDialog
from PySide6.QtGui import QTextDocument, QPainter, QPageSize, QPageLayout
from PySide6.QtCore import QMarginsF
from PySide6.QtCore import Qt
from models.doktori import get_all_doctors, get_doktor_isactive_by_color


class TiskRezervaci:
    """Třída pro tisk denních rezervací s barevnými kolečky doktorů."""
    
    def __init__(self, parent=None):
        self.parent = parent
    
    def tisk_aktualni_den(self, datum_str, rezervace, rezervace_doktoru, ordinace):
        """Hlavní funkce pro tisk aktuálního dne."""
        try:
            # Vytvoříme HTML obsah
            html_content = self._vytvor_html_pro_tisk(datum_str, rezervace, rezervace_doktoru, ordinace)
            
            # Nastavíme tiskárnu
            printer = QPrinter(QPrinter.HighResolution)
            printer.setPageOrientation(QPageLayout.Landscape)  # Landscape orientace
            printer.setPageSize(QPageSize.A4)
            
            # Zkusíme alternativní přístup pro okraje
            try:
                # Nastavíme minimální okraje
                layout = QPageLayout(QPageSize.A4, QPageLayout.Landscape, QMarginsF(1.0, 1.0, 1.0, 1.0), QPageLayout.Millimeter)
                printer.setPageLayout(layout)
            except Exception as e:
                print(f"Chyba při nastavování okrajů: {e}")
                # Fallback - použijeme starší metodu
                printer.setFullPage(True)
            
            # Zobrazíme dialog pro výběr tiskárny
            dialog = QPrintDialog(printer, self.parent)
            if dialog.exec() == QPrintDialog.Accepted:
                try:
                    # Vytvoříme dokument a nastavíme HTML
                    document = QTextDocument()
                    document.setHtml(html_content)
                    
                    # Nastavíme velikost stránky dokumentu podle tiskárny
                    document.setPageSize(printer.pageRect(QPrinter.DevicePixel).size())
                    
                    # Nastavíme větší default font pro dokument
                    font = document.defaultFont()
                    font.setPointSize(24)  # Ještě větší základní font
                    document.setDefaultFont(font)
                    
                    # Vytiskneme dokument - v PySide6 se používá print_()
                    document.print_(printer)
                    
                    if self.parent:
                        QMessageBox.information(self.parent, "Tisk", "Tisk byl úspěšně dokončen!")
                        
                except Exception as doc_error:
                    if self.parent:
                        QMessageBox.critical(self.parent, "Chyba tisku", f"Chyba při vytváření dokumentu: {str(doc_error)}")
            
        except Exception as e:
            if self.parent:
                QMessageBox.critical(self.parent, "Chyba tisku", f"Nastala chyba při tisku: {str(e)}")
            print(f"Chyba při tisku: {e}")

    def _vytvor_html_pro_tisk(self, datum_str, rezervace, rezervace_doktoru, ordinace):
        """Vytvoří HTML obsah pro tisk rezervací s barevnými kolečky doktorů."""
        
        # CENTRÁLNÍ NASTAVENÍ VELIKOSTÍ PÍSMA - CSS px hodnoty pro tisk
        FONT_SIZE_TITLE = "68px"          # Hlavní nadpis
        FONT_SIZE_HEADER = "50px"          # Hlavičky ordinací
        FONT_SIZE_TIME = "46px"            # Časy v tabulce
        FONT_SIZE_CONTENT = "46px"         # Obsah buněk s rezervacemi
        FONT_SIZE_LEGEND_TITLE = "50px"    # Nadpis legendy
        FONT_SIZE_LEGEND_TEXT = "46px"     # Text v legendě
        FONT_SIZE_LEGEND_CIRCLE = "68px"   # Kolečka v legendě
        FONT_SIZE_BASE = "50px"            # Základní velikost písma
        
        TIME_COLUMN_WIDTH = "260"        # Šířka sloupce s časy
        FONT_SIZE_TIME_CIRCLE = "68px"   # Velikost koleček v časovém sloupci

        BORDER_BOTTOM_COLOR = "#DFDFDF" # Barva spodní hranice buněk s rezervacemi


        # Seřadíme ordinace pro konzistentní pořadí (potřebujeme pro CSS)
        sorted_ordinace = sorted(ordinace)
        
        # Převedeme datum_str na datetime objekt pro porovnání
        datum_obj = datetime.strptime(datum_str, "%d.%m.%Y").date()
        
        # Zmapuj rezervace podle ordinace - data jsou už předfiltrovaná z databáze
        mapovane = {i: [] for i in ordinace}
        pocet_rezervaci = 0
        for r in rezervace:
            try:
                # Handle both datetime object (PostgreSQL) and string (SQLite) formats for r[0]
                if isinstance(r[0], datetime):
                    datum_db = r[0].strftime("%Y-%m-%d")
                else:
                    datum_db = str(r[0])
                    
                pocet_rezervaci += 1
                cas_od = datetime.strptime(f"{datum_db} {r[10]}", "%Y-%m-%d %H:%M")
                cas_do = datetime.strptime(f"{datum_db} {r[11]}", "%Y-%m-%d %H:%M")
                
                id = r[1]
                doktor = r[2] if r[2] else None
                doktor_color = r[3] if r[3] else None
                pacient = r[4] if r[4] else ""
                majitel = r[5] if r[5] else ""
                kontakt = r[6] if r[6] else ""
                druh = r[7] if r[7] else ""
                mistnost = r[8] if r[8] else ""
                poznamka = r[9] if r[9] else ""
                anestezie = r[12] if r[12] == True else None
                druhy_doktor = f"{r[13]}" if r[13] is not None else None
                barva_druhy_doktor = r[14] if r[14] is not None else None
                stav = r[15] if len(r) > 15 else None

                if mistnost and mistnost in mapovane:
                    mapovane[mistnost].append((cas_od, cas_do, id, doktor, doktor_color, pacient, majitel, kontakt, druh, poznamka, anestezie, druhy_doktor, barva_druhy_doktor, stav))
            except (ValueError, IndexError, AttributeError) as e:
                continue



        # Získáme mapování rozvrhu doktorů pro barevné kolečka
        rozvrh_doktoru_map = {}
        if rezervace_doktoru:
            for r in rezervace_doktoru:
                if r and len(r) > 6:
                    ordinace_nazev = r[6]  # název ordinace
                    if ordinace_nazev not in rozvrh_doktoru_map:
                        rozvrh_doktoru_map[ordinace_nazev] = []
                    rozvrh_doktoru_map[ordinace_nazev].append(r)

        # Vytvoř mapování doktorů podle barev pro rychlé vyhledávání
        doktori_podle_barev = {}
        try:
            all_doctors = get_all_doctors()  # Vrací: (doktor_id, jmeno, prijmeni, specializace, isActive, color)
            for doctor in all_doctors:
                if len(doctor) >= 6 and doctor[4] == 1:  # isActive == 1
                    color = doctor[5]  # color je na pozici 5
                    if color and color.strip() != "#ffffff":
                        doktori_podle_barev[color] = {
                            'id': doctor[0],
                            'jmeno': doctor[1],
                            'prijmeni': doctor[2],
                            'color': color
                        }
        except Exception as e:
            pass

        # Inicializujeme proměnné
        legend_html = ""
        sloupce_html = ""

        # Nejprve vygenerujeme data pro všechny ordinace a všechny časy
        ordinace_data = {}
        
        # Vytvoříme všechny časové sloty a data pro každou ordinaci
        for mistnost in sorted_ordinace:
            ordinace_data[mistnost] = []
            
            cas = datetime.combine(datum_obj, datetime.strptime("08:00", "%H:%M").time())
            end = datetime.combine(datum_obj, datetime.strptime("20:00", "%H:%M").time())
            
            while cas <= end:
                pause_time = False
                vaccination_time = False
                
                # Nastav slot podle času - STEJNÁ LOGIKA JAKO V APLIKACI
                if cas.time() >= datetime.strptime("09:00", "%H:%M").time() and cas.time() <= datetime.strptime("09:45", "%H:%M").time():
                    slot = timedelta(minutes=15)
                    vaccination_time = True
                elif cas.time() >= datetime.strptime("12:00", "%H:%M").time() and cas.time() < datetime.strptime("12:30", "%H:%M").time():
                    slot = timedelta(minutes=30)
                    pause_time = True
                elif cas.time() >= datetime.strptime("12:30", "%H:%M").time() and cas.time() < datetime.strptime("12:40", "%H:%M").time():
                    slot = timedelta(minutes=10)
                elif cas.time() == datetime.strptime("12:40", "%H:%M").time():
                    slot = timedelta(minutes=20)
                elif cas.time() >= datetime.strptime("16:00", "%H:%M").time() and cas.time() <= datetime.strptime("16:30", "%H:%M").time():
                    slot = timedelta(minutes=15)
                    vaccination_time = True
                elif cas.time() == datetime.strptime("16:45", "%H:%M").time():
                    slot = timedelta(minutes=35)
                    pause_time = True
                elif cas.time() >= datetime.strptime("17:20", "%H:%M").time():
                    slot = timedelta(minutes=20)
                else:
                    slot = timedelta(minutes=20)

                cas_str = cas.strftime("%H:%M")

                # Najdeme barvy doktorů pro tento čas a tuto konkrétní ordinaci
                doktor_circles = []
                if mistnost in rozvrh_doktoru_map and rozvrh_doktoru_map[mistnost]:
                    for r in rozvrh_doktoru_map[mistnost]:
                        try:
                            if r and len(r) > 5:
                                od = datetime.strptime(r[4], "%H:%M").time()
                                do = datetime.strptime(r[5], "%H:%M").time()
                                if od <= cas.time() <= do:
                                    doktor_active = get_doktor_isactive_by_color(r[2])
                                    if doktor_active == 1:
                                        barva = r[2].strip() if r[2] else "#ffffff"
                                        if barva != "#ffffff" and barva not in doktor_circles:
                                            doktor_circles.append(barva)
                        except (ValueError, IndexError, AttributeError) as e:
                            continue

                # Najdeme rezervace pro tento časový slot a tuto ordinaci
                rezervace_pro_cas = []
                if mistnost in mapovane:
                    for rez in mapovane[mistnost]:
                        cas_od, cas_do = rez[0], rez[1]  # tuple formát z aplikace
                        slot_end = cas + slot
                        
                        # Univerzální logika pro všechny typy rezervací
                        if cas_od < slot_end and cas_do >= cas:
                            rezervace_pro_cas.append(rez)

                # Získej barvy doktorů z rezervací pro tento čas
                for rez in rezervace_pro_cas:
                    # První doktor (index 4 je doktor_color)
                    if rez[4] and rez[4].strip() and rez[4].strip() != "#ffffff":
                        if rez[4].strip() not in doktor_circles:
                            doktor_circles.append(rez[4].strip())
                    # Druhý doktor (index 12 je barva_druhy_doktor)
                    if len(rez) > 12 and rez[12] and rez[12].strip() and rez[12].strip() != "#ffffff":
                        if rez[12].strip() not in doktor_circles and len(doktor_circles) < 2:
                            doktor_circles.append(rez[12].strip())

                # Vytvoř HTML pro kolečka v časové buňce - použijeme Unicode kolečka místo CSS
                time_circles_html = ""
                if doktor_circles:
                    circles_parts = []
                    for color in doktor_circles[:2]:  # Max 2 kolečka
                        # Použijeme Unicode kruhů s barevným HTML
                        circles_parts.append(f'<span style="color: {color}; font-size: {FONT_SIZE_TIME_CIRCLE} !important; font-weight: bold;">●</span>')
                    time_circles_html = f'{"".join(circles_parts)} '

                # Obsah buňky s rezervacemi
                content = ""
                if rezervace_pro_cas:
                    for i, rez in enumerate(rezervace_pro_cas):
                        if i > 0:
                            content += "<br>"
                        
                        # Základní info o rezervaci - stejný formát jako v aplikaci
                        parts = []
                        pacient = rez[5] if rez[5] else ""  # index 5 je pacient v tuple
                        majitel = rez[6] if rez[6] else ""   # index 6 je majitel
                        druh = rez[8] if rez[8] else ""      # index 8 je druh
                        poznamka = rez[9] if rez[9] else ""  # index 9 je poznamka
                        
                        if pacient:
                            parts.append(f"<b>{pacient}</b>")
                        if majitel:
                            parts.append(majitel)
                        if druh:
                            parts.append(f"({druh})")
                        
                        content += " ".join(parts)
                        
                        if poznamka:
                            content += f"<br><i>{poznamka}</i>"

                # Nastavení pozadí podle typu času
                row_bg = ""
                if pause_time:
                    row_bg = "background-color: #fff2cc;"  # Žluté pozadí pro pauzy
                elif vaccination_time:
                    row_bg = "background-color: #e1f5fe;"  # Modré pozadí pro vakcinace

                # Vytvoř řádek data pro tuto ordinaci
                time_content = f'{cas_str} {time_circles_html}' if time_circles_html else cas_str
                
                ordinace_data[mistnost].append({
                    'time_content': time_content,
                    'content': content if content else "&nbsp;",
                    'row_bg': row_bg
                })
                
                cas += slot
        
        # Vytvoříme sloupce pro každou ordinaci - pomocí starých HTML atributů
        sloupce_html = ""
        for mistnost in sorted_ordinace:
            sloupce_html += f"""<td width="25%" valign="top">
                        <table width="100%" border="0" cellpadding="4" cellspacing="1" style="border-collapse: separate;">
                            <tr height="40">
                                <th colspan="2" align="center" bgcolor="#e6f3ff" style="color: #0066cc; border: 1px solid #f0f0f0; padding: 15px 8px; height: 60px;"><div style="margin: 0; color: #0066cc; font-weight: bold; font-size: {FONT_SIZE_HEADER} !important;">{mistnost}</div></th>
                            </tr>"""
            
            # Přidáme všechny řádky pro tuto ordinaci
            for row_data in ordinace_data[mistnost]:
                bg_color = "#fff2cc" if "background-color: #fff2cc" in row_data['row_bg'] else "#e1f5fe" if "background-color: #e1f5fe" in row_data['row_bg'] else "#ffffff"
                
                sloupce_html += f"""
                            <tr height="30">
                                <td width="{TIME_COLUMN_WIDTH}" bgcolor="#f8f9fa" style="border-bottom: 1px solid {BORDER_BOTTOM_COLOR}; padding: 12px 8px; height: 50px;"><div style="margin: 0; font-weight: bold; font-size: {FONT_SIZE_TIME} !important;">{row_data['time_content']}</div></td>
                                <td bgcolor="{bg_color}" style="border-bottom: 1px solid #404040; padding: 12px 8px; height: 50px;"><div style="margin: 0; font-size: {FONT_SIZE_CONTENT} !important;">{row_data['content']}</div></td>
                            </tr>"""
            
            # Uzavřeme vnořenou tabulku pro tuto ordinaci
            sloupce_html += """
                        </table>
                    </td>"""

        # Vytvoříme legendu s doktory
        legend_html = ""
        try:
            all_doctors = get_all_doctors()
            legenda_items = []
            
            if all_doctors:
                for doctor in all_doctors:
                    if len(doctor) >= 6 and doctor[4] == 1:  # isActive == 1
                        jmeno = doctor[1] if doctor[1] else ""
                        prijmeni = doctor[2] if doctor[2] else ""
                        color = doctor[5] if doctor[5] else "#ffffff"
                        
                        # Přeskočíme bílé/prázdné barvy
                        if color and color.strip() != "#ffffff" and color.strip() != "":
                            celne_jmeno = f"{jmeno} {prijmeni}".strip()
                            if celne_jmeno:
                                legenda_items.append(f"""<span style="font-size: {FONT_SIZE_LEGEND_TEXT} !important;"><span style="color: {color}; font-weight: bold; font-size: {FONT_SIZE_LEGEND_CIRCLE} !important;">●</span> {celne_jmeno}</span>&nbsp;&nbsp;&nbsp;""")
                
                if legenda_items:
                    legend_html = f"""<div align="center" style="margin: 15px 0; padding: 10px;">
                        <div style="margin: 0 0 10px 0; font-weight: bold; font-size: {FONT_SIZE_LEGEND_TITLE} !important;">Legenda doktorů:</div>
                        {" ".join(legenda_items)}
                    </div>"""
        except Exception as e:
            legend_html = ""

        # Vytvoříme finální HTML s všemi daty
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rezervace - {datum_str}</title>
            <style>
                body {{
                    margin: 0;
                    padding: 0;
                    font-family: Arial, sans-serif;
                    font-size: {FONT_SIZE_BASE} !important;
                }}
                table {{
                    font-family: Arial, sans-serif;
                    font-size: {FONT_SIZE_BASE} !important;
                }}
                td, th {{
                    font-size: {FONT_SIZE_BASE} !important;
                }}
                div, span {{
                    font-size: inherit !important;
                }}
                * {{
                    font-size: inherit !important;
                }}
            </style>
        </head>
        <body>
            <div style="text-align: center; margin: 20px 0; font-weight: bold; font-size: {FONT_SIZE_TITLE} !important;">Rezervace pro {datum_str}</div>
            <table width="100%" border="0" cellpadding="0" cellspacing="0">
                <tr>
                    {sloupce_html}
                </tr>
            </table>
            {legend_html}
        </body>
        </html>
        """
        
        return html
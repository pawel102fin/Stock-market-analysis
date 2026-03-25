from fpdf import FPDF
from datetime import datetime

class PelnyRaport(FPDF):
    def header(self):
        # Nagłówek
        self.set_font('Arial', 'B', 14)
        self.cell(100, 10, 'Raport Gieldowy', 0, 0, 'L')
        
        self.set_font('Arial', '', 10)
        self.cell(0, 10, datetime.now().strftime("%Y-%m-%d"), 0, 1, 'R')
        
        # Linia oddzielająca
        self.line(10, 20, 200, 20)
        self.ln(15) # Duży odstęp po nagłówku

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Strona {self.page_no()}', 0, 0, 'C')

    def pl(self, t):
        # Funkcja naprawiająca polskie znaki
        if not t: return ""
        m = {'ą':'a','ć':'c','ę':'e','ł':'l','ń':'n','ó':'o','ś':'s','ź':'z','ż':'z',
             'Ą':'A','Ć':'C','Ę':'E','Ł':'L','Ń':'N','Ó':'O','Ś':'S','Ź':'Z','Ż':'Z'}
        for k,v in m.items(): t = t.replace(k,v)
        return t

def generuj_pdf(ticker, dane, sciezka, wynik):
    pdf = PelnyRaport()
    pdf.add_page()

    # --- 1. TYTUŁ I CENA ---
    pdf.set_font('Arial', 'B', 24)
    # Tytuł
    pdf.cell(0, 15, f"{ticker}", 0, 1, 'L')
    
    # Cena mniejszą czcionką pod spodem
    pdf.set_font('Arial', '', 16)
    pdf.cell(0, 10, f"Cena aktualna: {dane['Cena']}", 0, 1, 'L')
    pdf.ln(5)

    # --- 2. WERDYKT ---
    pdf.set_font('Arial', 'B', 16)
    rek = dane.get('Rekomendacja','-')
    
    if "KUPUJ" in rek: pdf.set_text_color(0, 128, 0)   # Ciemny zielony
    elif "SPRZEDAJ" in rek: pdf.set_text_color(178, 34, 34) # Ciemny czerwony
    else: pdf.set_text_color(0,0,0)
    
    # Wypisujemy werdykt
    tekst_werdyktu = pdf.pl(f"DECYZJA: {rek} ({dane['Punkty']} pkt)")
    pdf.cell(0, 10, tekst_werdyktu, 0, 1, 'L')
    
    # Reset koloru na czarny
    pdf.set_text_color(0,0,0)
    pdf.ln(10)

    # --- 3. TABELA WSKAŹNIKÓW (Metoda Wiersz po Wierszu) ---
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, "Tablica Wskaznikow:", 0, 1)
    
    # Ustawiamy czcionkę dla tabeli
    pdf.set_font('Arial', '', 11)
    
    # Lista lewa
    lewa = [
        f"Kapitalizacja: {dane['Kapitalizacja']}",
        f"EV: {dane['EV']}",
        f"P/E: {dane['PE']}",
        f"PEG: {dane['PEG']}",
        f"P/B: {dane['PB']}",
        f"EV/EBITDA: {dane['EV_EBITDA']}"
    ]
    
    # Lista prawa
    prawa = [
        f"ROE: {dane['ROE']}",
        f"Marza Zysku: {dane['Marza_Zysku']}",
        f"Marza EBITDA: {dane['Marza_EBITDA']}",
        f"Wzrost Rev: {dane['Wzrost_Rev']}",
        f"Wzrost Earn: {dane['Wzrost_Earn']}",
        f"FCF Yield: {dane['FCF_Yield']}"
    ]

    # Rysujemy parami (Lewy element, potem Prawy element w tej samej linii)
    szerokosc_kolumny = 95 # Polowa strony (prawie)
    wysokosc_wiersza = 8
    
    for l_item, p_item in zip(lewa, prawa):
        # Komórka lewa (bez przechodzenia do nowej linii -> ln=0)
        pdf.cell(szerokosc_kolumny, wysokosc_wiersza, l_item, border=0, ln=0)
        
        # Komórka prawa (przejście do nowej linii -> ln=1)
        pdf.cell(szerokosc_kolumny, wysokosc_wiersza, p_item, border=0, ln=1)

    pdf.ln(10) # Odstęp po tabeli

    # --- 4. OPISY SŁOWNE ---
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, "Analiza Fundamentalna:", 0, 1)
    
    pdf.set_font('Arial', '', 11)
    # Multi_cell zawija tekst automatycznie, więc nie wyjedzie poza margines
    pdf.multi_cell(0, 6, pdf.pl(dane['Opis_Fund']))
    
    pdf.ln(5)
    
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, "Analiza Techniczna:", 0, 1)
    pdf.set_font('Arial', '', 11)
    pdf.multi_cell(0, 6, pdf.pl(dane['Opis_Tech']))

    # --- 5. WYKRES ---
    pdf.ln(10)
    try:
        # Skalujemy wykres, żeby na pewno się zmieścił (w=170 mm)
        pdf.image(sciezka, x=15, w=170)
    except:
        pdf.cell(0, 10, "Brak wykresu", 0, 1)

    pdf.output(wynik)
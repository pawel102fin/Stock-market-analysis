import os  # Importuje moduł systemu operacyjnego (np. do sprawdzania folderów).
import analiza  # Importuje plik z obliczeniami (ten powyżej).
import market_data  # Importuje plik do pobierania danych z Yahoo.
import plotter  # Importuje plik do rysowania wykresów.
import pdf_generator  # Importuje plik do tworzenia PDF-ów.
import data_loader  # Importuje plik do wczytywania Excela.

# Funkcja pomocnicza do ładnego formatowania liczb.
def formatuj_liczbe(wartosc, dopisek="", skrot_dla_duzych=False):
    if wartosc is None: return "-" 
    if skrot_dla_duzych:  
        if wartosc > 1e9: return f"{round(wartosc/1e9, 2)} mld"  # Powyżej miliarda 
        if wartosc > 1e6: return f"{round(wartosc/1e6, 2)} mln"  # Powyżej miliona 
    return f"{round(wartosc, 2)}{dopisek}"

# Funkcja pomocnicza do formatowania procentów.
def formatuj_procent(wartosc):
    if wartosc is None: return "-"  
    return f"{round(wartosc*100, 2)}%" 
#Główna pętla
def uruchom_analize():
    
    lista_spolek = data_loader.wczytaj_tickery('spolki.xlsx')
    
    if not lista_spolek:
        print("Brak spółek do analizy.")
        return 

    if not os.path.exists('temp_wykresy'):
        os.makedirs('temp_wykresy') 


    for symbol in lista_spolek:
        try:  
            
            # 1.POBIERANIE DANYCH
            tabela_cen = market_data.pobierz_historie(symbol)
            # Pobieramy dane fundamentalne
            dane_fundamentalne = market_data.pobierz_fundamenty(symbol)
            
            # --- Mechanizm naprawczy dla polskich spółek ---
            # Yahoo czasem nie podaje aktualnej ceny ('Cena' jest puste), ale daje historię.
            cena_z_fundamentow = dane_fundamentalne.get('Cena') 
            
            # Jeśli ceny nie ma (lub jest 0) ORAZ mamy tabelę z historią:
            if (not cena_z_fundamentow or cena_z_fundamentow == 0) and not tabela_cen.empty:
                ostatnia_zamkniecia = tabela_cen['Close'].iloc[-1]  # Bierzemy ostatnią cenę z wykresu.
                dane_fundamentalne['Cena'] = round(ostatnia_zamkniecia, 2)
            
            # Ostateczne sprawdzenie: czy mamy tabelę ORAZ czy mamy cenę
            if tabela_cen.empty or not dane_fundamentalne['Cena']:
                print(f"Pominięto {symbol} - brak danych.")
                continue  #następna spółka

            # 2. ANALIZA
            # Wysyłamy tabelę cen do analizy.py i odbieramy wyniki techniczne (RSI).
            wynik_techniczny = analiza.oblicz_wskazniki_techniczne(tabela_cen)
            # Wysyłamy tabelę cen do analizy.py i odbieramy obliczone ryzyko.
            ryzyko = analiza.oblicz_ryzyko_roczne(tabela_cen)
            # Wysyłamy fundamenty do analizy.py i odbieramy wielki słownik z oceną ("MOCNE KUPUJ" itp.).
            wynik_fundamentalny = analiza.ocen_fundamenty(dane_fundamentalne)

            # 3. PRZYGOTOWANIE RAPORTU
            # Łączymy listę powodów (tekstów) w jeden długi ciąg znaków oddzielony przecinkami.
            tekst_uzasadnienia = ", ".join(wynik_fundamentalny['uzasadnienie'])
            
            # Jeśli lista powodów była pusta, wpisujemy domyślny tekst.
            if not tekst_uzasadnienia:
                tekst_uzasadnienia = "Brak silnych sygnałów."

            # Tworzymy słownik 'raport', który przekażemy do generatora PDF.
            # Mapujemy (przypisujemy) nasze obliczone zmienne do nazw, które zrozumie PDF.
            raport = {
                'Symbol': symbol,
                'Cena': f"{dane_fundamentalne['Cena']} PLN",  # Dodajemy dopisek PLN.
                
                # Tu wyciągamy dane ze słownika, który zwróciła funkcja ocen_fundamenty.
                'Rekomendacja': wynik_fundamentalny['decyzja'], 
                'Punkty': wynik_fundamentalny['punkty'],
                'FCF_Yield': formatuj_liczbe(wynik_fundamentalny['fcf_yield'], "%"),
                
                # Formatujemy resztę liczb naszymi funkcjami pomocniczymi.
                'Kapitalizacja': formatuj_liczbe(dane_fundamentalne['Kapitalizacja'], skrot_dla_duzych=True),
                'EV': formatuj_liczbe(dane_fundamentalne['EV'], skrot_dla_duzych=True),
                'PE': formatuj_liczbe(dane_fundamentalne['PE']),
                'PEG': formatuj_liczbe(dane_fundamentalne['PEG']),
                'PB': formatuj_liczbe(dane_fundamentalne['PB']),
                'EV_EBITDA': formatuj_liczbe(dane_fundamentalne['EV_EBITDA']),
                
                'ROE': formatuj_procent(dane_fundamentalne['ROE']),
                'Marza_Zysku': formatuj_procent(dane_fundamentalne['Marza_Zysku']),
                'Marza_EBITDA': formatuj_procent(dane_fundamentalne['Marza_EBITDA']),
                
                'Wzrost_Rev': formatuj_procent(dane_fundamentalne['Wzrost_Przychodow']),
                'Wzrost_Earn': formatuj_procent(dane_fundamentalne['Wzrost_Zyskow']),

                'Opis_Fund': tekst_uzasadnienia,
                'Opis_Tech': f"RSI: {round(wynik_techniczny['RSI'],1)}. Zmienność: {ryzyko}%.",
            }

            # 4. GENEROWANIE PLIKÓW
            sciezka_wykresu = f"temp_wykresy/{symbol}.png"

            plotter.generuj_wykres(symbol, tabela_cen, sciezka_wykresu)
            
        
            pdf_generator.generuj_pdf(symbol, raport, sciezka_wykresu, f'Raport_{symbol}.pdf')
            
            print(f"SUKCES: Wygenerowano raport dla {symbol}") 

        except Exception as e:  
            print(f"BŁĄD przy {symbol}: {e}")  
            continue

if __name__ == "__main__":  # Ta linijka sprawdza, czy plik jest uruchamiany bezpośrednio (kliknięty).
    uruchom_analize()  # Jeśli tak, uruchom główną funkcję.
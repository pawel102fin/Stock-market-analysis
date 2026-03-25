import pandas as pd 
import numpy as np  

#KONFIGURACJA STRATEGII
LIMIT_PE_TANIO = 15  #P/E poniżej 15 uznajemy za "tanio".
LIMIT_PE_DROGO = 40  #P/E powyżej 40 uznajemy za "bardzo drogo".
LIMIT_PEG_OKAZJA = 1.0  # PEG poniżej 1.0 to super okazja.
WYMAGANY_WZROST_PRZYCHODOW = 0.10  # Oczekujemy wzrostu przychodów o min. 10% (0.10).
WYMAGANY_ROE = 0.15  # Oczekujemy zwrotu z kapitału (ROE) na poziomie min. 15% (0.15).

def oblicz_wskazniki_techniczne(tabela_cen):  # Definiujemy funkcję, która przyjmuje tabelę z cenami historycznymi.
    #200dni
    if tabela_cen is None or len(tabela_cen) < 200:
        return None
        
    # Tworzymy kopię tabeli, pracujemy na kopii 'df'.
    df = tabela_cen.copy()
    
    # --- 1. Obliczanie RSI (Wskaźnik siły względnej) ---
    zmiana_ceny = df['Close'].diff()  # Oblicza różnicę ceny: "cena dzisiaj minus cena wczoraj".
    
    # Rozdzielamy zmiany na wzrosty i spadki:
    wzrosty = zmiana_ceny.clip(lower=0)  
    spadki = -1 * zmiana_ceny.clip(upper=0) #usuwamy minus 
    
    #średnia wykładnicza z ostatnich 14 dni (com=13).
    srednia_wzrostow = wzrosty.ewm(com=13, adjust=False).mean()  
    srednia_spadkow = spadki.ewm(com=13, adjust=False).mean()
    
    sila_relatywna = srednia_wzrostow / srednia_spadkow
    
    df['RSI'] = 100 - (100 / (1 + sila_relatywna))
    
    # --- 2. Obliczanie średnich kroczących (SMA) ---
    df['SMA50'] = df['Close'].rolling(window=50).mean()
    df['SMA200'] = df['Close'].rolling(window=200).mean()
    
    #Koniec funkcji - dane z dzisiaj/wczoraj
    return df.iloc[-1]

def oblicz_ryzyko_roczne(tabela_cen): 
    if tabela_cen is None or tabela_cen.empty:
        return 0
    
    #zmianq procentowa ceny dzień do dnia. '.dropna()' usuwa pierwszy dzień
    procentowe_zmiany = tabela_cen['Close'].pct_change().dropna()
    
    #odchylenie standardowe.
    odchylenie = procentowe_zmiany.std()
    
    #ryzyko dzienne na roczne mnożymy przez pierwiastek z 252 - liczba sesji giełdowych w roku.
    ryzyko_roczne = round(odchylenie * np.sqrt(252) * 100, 2)
    
    return ryzyko_roczne 

def ocen_fundamenty(dane_finansowe): 
    punkty = 0  
    lista_powodow = [] #textowe uzasadnienia
    
    # .get('Klucz') jest bezpieczne - jeśli klucza nie ma, zwróci None 
    pe = dane_finansowe.get('PE')
    peg = dane_finansowe.get('PEG')
    pb = dane_finansowe.get('PB')
    roe = dane_finansowe.get('ROE')
    wzrost_przychodow = dane_finansowe.get('Wzrost_Przychodow')
    fcf = dane_finansowe.get('FCF')
    kapitalizacja = dane_finansowe.get('Kapitalizacja')

    # --- KROK 1: OCENA WYCENY ---
    if pe: 
        if 0 < pe < LIMIT_PE_TANIO:  
            punkty += 1 
            lista_powodow.append(f"Spółka tania (P/E {round(pe,1)} < {LIMIT_PE_TANIO})")
        elif pe > LIMIT_PE_DROGO:  
            punkty -= 1  
            lista_powodow.append(f"Spółka bardzo droga (P/E {round(pe,1)})")
            
    if peg and 0 < peg < LIMIT_PEG_OKAZJA: 
        punkty += 2  
        lista_powodow.append(f"Super okazja wzrostowa (PEG {peg} < 1)")

    if pb and pb < 1.5:  
        punkty += 1 
        lista_powodow.append(f"Wycena poniżej wartości majątku (P/B {round(pb,1)})")

    # --- KROK 2: OCENA JAKOŚCI BIZNESU ---
    if roe and roe > WYMAGANY_ROE:  
        punkty += 1  
        lista_powodow.append(f"Wysoka rentowność kapitału (ROE {round(roe*100,1)}%)")

    if wzrost_przychodow and wzrost_przychodow > WYMAGANY_WZROST_PRZYCHODOW:  
        punkty += 1  
        lista_powodow.append(f"Firma rośnie (Przychody +{round(wzrost_przychodow*100,1)}% r/r)")

    # --- KROK 3: PRZEPŁYWY PIENIĘŻNE---
    fcf_yield = 0 
    if fcf and kapitalizacja and kapitalizacja > 0:  # Musimy mieć FCF i dodatnią kapitalizację, żeby dzielić.
        fcf_yield = (fcf / kapitalizacja) * 100  # Obliczamy ile gotówki generuje firma względem swojej ceny (Yield).
        if fcf_yield > 4.0:  # Jeśli generuje powyżej 4% swojej wartości w gotówce rocznie.
            punkty += 1  # Punkt za bezpieczeństwo gotówkowe.
            lista_powodow.append(f"Firma generuje gotówkę (FCF Yield {round(fcf_yield,1)}%)")

    # --- KROK 4: WERDYKT KOŃCOWY ---
    if punkty >= 6: decyzja = "MOCNE KUPUJ"
    elif punkty >= 3: decyzja = "KUPUJ"
    elif punkty >= 0: decyzja = "TRZYMAJ"
    else: decyzja = "SPRZEDAJ"  

    # Tworzymy słownik (paczkę danych), w którym wszystko ładnie nazywamy.
    wynik_analizy = {
        'decyzja': decyzja,          # Tu wkładamy tekst "KUPUJ" itp.
        'punkty': punkty,            # Tu wkładamy liczbę punktów.
        'uzasadnienie': lista_powodow, # Tu wkładamy listę tekstów z powodami.
        'fcf_yield': fcf_yield       # Tu wkładamy obliczony procent FCF.
    }
    
    return wynik_analizy  # Funkcja zwraca ten słownik do pliku main.py.
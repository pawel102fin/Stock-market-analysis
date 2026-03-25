# Stock Market Analysis 

Narzędzie w języku Python służące do automatycznej analizy technicznej spółek giełdowych. Program wczytuje zdefiniowaną listę spółek z pliku Excel, pobiera ich notowania z ostatniego roku, oblicza wskaźnik RSI, generuje wykresy, a następnie tworzy gotowy raport w formacie PDF.

## Funkcjonalności

* **Import z Excela:** Wczytywanie listy tickerów giełdowych z pliku `spolki.xlsx`.
* **Pobieranie danych rynkowych:** Automatyczne pobieranie historycznych notowań z ostatniego roku (1y) za pomocą Yahoo Finance API (`yfinance`).
* **Analiza techniczna:** Obliczanie 14-dniowego wskaźnika siły względnej (RSI - Relative Strength Index).
* **Wizualizacja danych:** Generowanie czytelnych wykresów dla każdej spółki, zawierających cenę zamknięcia (Close Price) oraz oscylator RSI w osobnych panelach.
* **Generowanie PDF:** Automatyczne składanie wygenerowanych wykresów w jeden zbiorczy plik `Stock_Analysis_Report.pdf`.

## Struktura projektu

Projekt został podzielony na moduły, z których każdy ma jedno, konkretne zadanie:

* `main.py` - Główny skrypt uruchamiający program. Przechodzi przez wszystkie etapy: od pobrania listy po zapis PDF.
* `spolki.xlsx` - Plik wejściowy. Zawiera kolumnę "Ticker" z symbolami giełdowymi (np. AAPL, MSFT, GOOGL).
* `data_loader.py` - Używa biblioteki *pandas* do poprawnego odczytania tickerów z Excela.
* `market_data.py` - Integruje się z API *yfinance* i ściąga notowania.
* `analiza.py` - Implementuje algorytm obliczający wskaźnik RSI na podstawie cen zamknięcia.
* `plotter.py` - Korzysta z *matplotlib*, aby wyrysować podwójny wykres i zapisać go jako plik PNG.
* `pdf_generator.py` - Korzysta z biblioteki *fpdf*, tworząc stronę tytułową i wklejając wszystkie wygenerowane wykresy do jednego dokumentu PDF.

## Wymagania i instalacja

Aby uruchomić projekt, musisz zainstalować środowisko Python oraz kilka zewnętrznych bibliotek. Otwórz terminal w folderze projektu i wpisz poniższą komendę:

```bash
pip install pandas yfinance matplotlib fpdf openpyxl

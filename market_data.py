import yfinance as yf
import pandas as pd

def pobierz_historie(ticker):
    try:
        spolka = yf.Ticker(ticker)
        return spolka.history(period="2y")
    except:
        return pd.DataFrame()

def pobierz_fundamenty(ticker):
    info = {}
    try:
        spolka = yf.Ticker(ticker)
        info = spolka.info
    except:
        pass # Cisza w razie błędu połączenia

    def get_num(key):
        val = info.get(key)
        return val if val is not None else 0

    dane = {
        'Cena': info.get('currentPrice', info.get('regularMarketPreviousClose', 0)),
        'Kapitalizacja': get_num('marketCap'),
        'PE': info.get('trailingPE'),
        'PEG': info.get('pegRatio'),
        'PB': info.get('priceToBook'),
        'EV': get_num('enterpriseValue'),
        'EV_EBITDA': info.get('enterpriseToEbitda'),
        'ROE': info.get('returnOnEquity'),
        'Marza_Zysku': info.get('profitMargins'),
        'Marza_EBITDA': info.get('ebitdaMargins'),
        'Wzrost_Przychodow': info.get('revenueGrowth'),
        'Wzrost_Zyskow': info.get('earningsGrowth'),
        'FCF': get_num('freeCashflow')
    }
    return dane
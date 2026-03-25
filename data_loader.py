import pandas as pd
import os

def wczytaj_tickery(sciezka='spolki.xlsx'):
    if not os.path.exists(sciezka):
        return [] # Brak pliku = koniec pracy bez słowa

    try:
        df = pd.read_excel(sciezka, header=None)
        lista = df.iloc[:, 0].astype(str).tolist()
        lista_oczyszczona = [
            x.strip().upper() 
            for x in lista 
            if x.lower() != 'nan' and len(x.strip()) > 0
        ]
        return lista_oczyszczona
    except:
        return []
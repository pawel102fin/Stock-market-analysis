import matplotlib.pyplot as plt

def generuj_wykres(ticker, historia, sciezka):
    plt.figure(figsize=(10,5))
    plt.plot(historia.index, historia['Close'])
    plt.title(f'Historia ceny: {ticker}')
    plt.xlabel('Data')
    plt.ylabel('Cena zamknięcia')
    plt.tight_layout()
    plt.savefig(sciezka)
    plt.close()

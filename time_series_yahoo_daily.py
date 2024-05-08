import yfinance as yf
import numpy as np
import pandas as pd
import requests
from bs4 import BeautifulSoup, SoupStrainer

def clean_links(links):
    clean_links_array = []
    for link in links:
        if "quote" in link and "-USD" in link:
            clean_links_array.append(link.replace("/quote/",""))

    return clean_links_array

def gather_links(response):
    """
    Returns a list of links observed within the response input
    """
    links = []

    for link in BeautifulSoup(response.content, parse_only=SoupStrainer('a')):
        try:
            if link.has_attr('href'):
                links.append(link['href'])

        except AttributeError:
            pass

    return links

symbols = []

for offset in np.arange(0,9900,100):
    url = f"https://finance.yahoo.com/screener/predefined/all_cryptocurrencies_us/?count=100&offset={offset}"

    resp = requests.get(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36"
        },
    )

    links = gather_links(resp)

    clean_links_array = clean_links(links)

    symbols = symbols + clean_links_array

symbols_bis = symbols.copy()
symbols = []
for x in symbols_bis:
    if x not in symbols:
        symbols.append(x)

stablecoins = list(pd.read_csv('stablecoins.csv').keys())
stablecoins = list(map(lambda x: x.lower(), stablecoins))

symbol_non_stablecoins = []
symbol_stablecoins     = []

for symbol in symbols:

    cmp = symbol.replace("-USD", "").lower()
    if cmp in stablecoins:
        symbol_stablecoins.append(symbol)
    else:
        symbol_non_stablecoins.append(symbol)

print(f"Num non stable coins: {len(symbol_non_stablecoins)}")
print(f"Num non stable coins: {len(symbol_stablecoins)}")

i = 0
for symbol in symbols:
    msft = yf.Ticker(symbol)
    temp_data = msft.history(period="max")

    if temp_data.empty:
        i+=1
        continue

    nrows = temp_data.shape[0]
    ticker = [symbol] * nrows
    temp_data = temp_data.drop(columns = ['Dividends', "Stock Splits"])
    temp_data['close_times_volume'] = temp_data['Close'] * temp_data['Volume']
    temp_data['Ticker'] = ticker
    temp_data['Date'] = temp_data.index

    if symbol in symbol_stablecoins:
        temp_data['stablecoin'] = [True]  * nrows
    else:
        temp_data['stablecoin'] = [False] * nrows

    if i == 0:
        data = temp_data.copy()
    else:
        data = pd.concat([data, temp_data],axis = 0)

    i+=1

compression_opts = dict(method='zip',
                        archive_name='data_crypto_25_april.csv')
data.to_csv('data_crypto_25_april.zip', index=False,
          compression=compression_opts)

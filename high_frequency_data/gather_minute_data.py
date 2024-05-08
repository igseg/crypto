import requests
import re
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from bs4 import BeautifulSoup, SoupStrainer
from bs4.element import Comment
from datetime import datetime
from unicodedata import normalize
from time import mktime
import csv
import json
import sys

sys.path.append('/home/ignacio/Documents/SFU/crypto/textual_analysis')
from tools_scrapping import gather_links, clean_links

FIELDNAMES = [
 'high', 'close', 'timestamp', 'low', 'open'
]

params = {
    "region": "US",
    "lang": "en-US",
    "includePrePost": False,
    "interval": "1m" ,
    "useYfid": True,
    "range": "5d",
    "corsDomain": "finance.yahoo.com",
    ".tsrc": "finance",
}

path = "/media/hdd/crypto/data_yahoo/"

symbols = []
offset = 0
while True:
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

    if not resp.ok:
        break

    offset += 100


symbols_bis = symbols.copy()
symbols = []
for x in symbols_bis:
    if x not in symbols:
        symbols.append(x)


for symbol in symbols:

    # print(symbol)

    url = "https://query1.finance.yahoo.com/v8/finance/chart/" + symbol

    resp = requests.get(
        url,
        params=params,
        headers={
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36"
        },
    )

    result_dict = resp.json().get("chart", dict()).get("result")[0]
    timestamps = result_dict.get("timestamp")
    quote_dict = result_dict.get("indicators").get("quote")[0]
    quote_dict['timestamp'] = timestamps

    if quote_dict['timestamp'] == None:
        continue

    data = pd.DataFrame.from_dict (quote_dict)
    data = data[['timestamp', 'low', 'open', 'high', 'volume', 'close']]

    filename = path + symbol + ".csv"

    try:
        data_or = pd.read_csv(filename)
        data = pd.concat([data_or,data]).drop_duplicates()

    except FileNotFoundError:
        pass

    data.to_csv(filename, index = False)

    if symbol == "BTC-USD":
        df = pd.read_csv(filename)
        df.timestamp.plot()
        plt.show()
        del df

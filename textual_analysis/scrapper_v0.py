import requests
import re
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from bs4 import BeautifulSoup, SoupStrainer
from bs4.element import Comment
from datetime import datetime
from unicodedata import normalize
import httplib2
import time

from tools_scrapping import *


url = 'https://www.coindesk.com/'
max_time_running = 600

starting_time = time.time()
current_time  = time.time()
time_elapsed  = current_time - starting_time

time_checks = 10
time_step   = max_time_running/time_checks
step = 0

non_analyzed_links = set()
analyzed_links = set()

non_analyzed_links.add(url)

while non_analyzed_links != {} and time_elapsed < max_time_running:

    local_url = non_analyzed_links.pop()
    response = requests.get(local_url)

    ## Assess that we recieved a response

    if not response.ok:
        print('Error recieving a response')

    ## Gather and classify the links observed in the response

    links = gather_links(response)
    links = add_root(links, url)
    links = drop_external_links(links, url)

    for link in links:
        if link in analyzed_links:
            continue
        elif url in link:
            non_analyzed_links.add(link[:-1])

    del links

    ## Gather and save the content observed within the response

    soup = BeautifulSoup(response.content, "html.parser")

    ## Gather textual data

    texts = soup.findAll(text=True)
    visible_texts_bis = list(filter(tag_visible, texts)).copy()
    visible_texts_bis = map(remove_special_chars, visible_texts_bis)
    visible_texts = []
    [visible_texts.append(x) for x in visible_texts_bis if x not in visible_texts]
    visible_texts = np.array(visible_texts)

    if visible_texts.size == 0:
        continue

    chars = map(lambda x: len(x), visible_texts)
    chars = np.fromiter(chars, dtype=int)
    thershold = np.quantile(chars, q = 0.8)
    visible_texts = visible_texts[chars > thershold]


    ## Gather date, this is specific for coindesk:

    try:
        date = soup.find_all("meta", attrs={"property": "article:published_time"})[0]['content']
    except IndexError:
        continue

    timestamp = str(string_to_timestamp_coindesk(date))

    visible_texts = np.concatenate(([str(timestamp)], visible_texts))

    ## Save data

    local_url = local_url.replace('/','-')
    filename = f'Data/{local_url}.npy'

    if len(filename) > 50:
        filename = filename[:50]

    np.save(filename, visible_texts)

    ## updates for the next iteration
    
    analyzed_links.add(local_url)

    current_time  = time.time()
    time_elapsed  = current_time - starting_time

    if time_elapsed > time_step * step:
        step += 1
        print(f"Number non analyzed documents: {len(non_analyzed_links)}")
        print(f"Number analyzed documents: {len(analyzed_links)}")
        print("="*70)

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

def add_root(links, url):
    for idx, link in enumerate(links):
        if 'http' not in link:
            links[idx] = url + link

    return links

def drop_external_links(links, url):
    for idx, link in enumerate(links):
        if url not in link:
            links.remove(link)

    return links

def tag_visible(element):
    if element.parent.name in ['style', 'script', 'head', 'title', 'meta', '[document]']:
        return False
    if isinstance(element, Comment):
        return False
    return True

remove_special_chars = lambda string: re.sub(r"[^a-zA-Z0-9]+", ' ', string)

def clean_links(links):
    clean_links_array = []
    for link in links:
        if "quote" in link and "-USD" in link:
            clean_links_array.append(link.replace("/quote/",""))

    return clean_links_array

def string_to_timestamp_coindesk(date_string):
    # Define format strings with and without milliseconds
    format_with_ms = '%Y-%m-%dT%H:%M:%S.%fZ'
    format_without_ms = '%Y-%m-%dT%H:%M:%SZ'

    try:
        # Try parsing with milliseconds
        date_object = datetime.strptime(date_string, format_with_ms)
    except ValueError:
        # If milliseconds are not present, parse without milliseconds
        date_object = datetime.strptime(date_string, format_without_ms)

    # Convert datetime object to timestamp
    timestamp = date_object.timestamp()
    return timestamp

def load_links(path_non_analyzed_links = 'non_analyzed_links.npy', path_analyzed_links = 'analyzed_links.npy'):
    try:
        non_analyzed_links = np.load(path_non_analyzed_links)
    except FileNotFoundError:
        non_analyzed_links = np.array([], dtype=str)

    try:
        analyzed_links = np.load(path_analyzed_links)
    except FileNotFoundError:
        analyzed_links = np.array([], dtype=str)

    return set(analyzed_links), set(non_analyzed_links)

def save_links(non_analyzed_links, analyzed_links, path_non_analyzed_links = 'non_analyzed_links.npy', path_analyzed_links = 'analyzed_links.npy'):
    np.save(path_non_analyzed_links, np.array(non_analyzed_links))
    np.save(path_analyzed_links    , np.array(analyzed_links)    )
    return None

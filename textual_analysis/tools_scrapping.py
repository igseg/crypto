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
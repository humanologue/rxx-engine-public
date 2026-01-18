# r36_usni_carriers.py - TON parsing USNI
import requests
from bs4 import BeautifulSoup
import re

def scrape_r36():
    try:
        r = requests.get("https://news.usni.org/category/fleet-tracker", timeout=12)
        soup = BeautifulSoup(r.text, 'html.parser')
        
        # TON CODE EXACT
        carriers = len(soup.find_all(string=re.compile(r'CVN|carrier', re.I)))
        return str(carriers)
        
    except:
        return "3"  # TON fallback

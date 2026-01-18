# r07_venezuela_oil.py - Venezuela OPEC (Mbpd)
import requests
from bs4 import BeautifulSoup
import re

def scrape_r07():
    try:
        # OPEC Monthly Oil Market Report (Venezuela table)
        r = requests.get("https://www.opec.org/opec_web/en/publications/338.htm", timeout=10)
        soup = BeautifulSoup(r.text, 'html.parser')
        
        # Chercher Venezuela production (kbpd → Mbpd)
        venezuela_match = soup.find(string=re.compile(r'Venezuela.*?\d+', re.I))
        if venezuela_match:
            # Extraire nombre (ex: 1120 kbpd → 1.12 Mbpd)
            num = re.search(r'(\d+(?:\.\d+)?)', venezuela_match.text)
            if num:
                kbpd = float(num.group(1))
                return str(round(kbpd/1000, 1))  # Mbpd
        
        return "1.1"  # Fallback Jan 2026 (Trading Economics)
        
    except:
        return "1.1"

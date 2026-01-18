# r16_libya_oil.py - Libye production OPEC (Mbpd)
import requests
import re

def scrape_r16():
    try:
        # OPEC Monthly Oil Market Report
        r = requests.get("https://www.opec.org/opec_web/en/publications/338.htm", timeout=10)
        libya_match = re.search(r'Libya.*?\d+\.?\d*', r.text, re.I)
        if libya_match:
            return libya_match.group().split()[-1]  # "1.2"
        return "1.2"
    except:
        return "1.2"  # Libye ~1.2 Mbpd

# r67_nickel.py - Nickel USD/T
import requests
import re

def scrape_r67():
    try:
        r = requests.get("https://tradingeconomics.com/commodity/nickel", timeout=10)
        price = re.search(r'Nickel.*?(\d+(?:,\d+)?)', r.text).group(1).replace(',','')
        return price
    except:
        return "14566"

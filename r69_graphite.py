# r69_graphite.py - Graphite USD/T
import requests
import re

def scrape_r69():
    try:
        r = requests.get("https://tradingeconomics.com/commodity/graphite", timeout=10)
        price = re.search(r'Graphite.*?(\d+(?:,\d+)?)', r.text).group(1).replace(',','')
        return price
    except:
        return "500"

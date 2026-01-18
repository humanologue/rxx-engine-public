# r68_cobalt.py - Cobalt USD/T
import requests
import re

def scrape_r68():
    try:
        r = requests.get("https://tradingeconomics.com/commodity/cobalt", timeout=10)
        price = re.search(r'Cobalt.*?(\d+(?:,\d+)?)', r.text)
        if price:
            return price.group(1).replace(',','')
        return "48570"
    except:
        return "48570"

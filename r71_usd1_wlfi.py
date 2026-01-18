# dags/r71_usd1_wlfi.py
import re
import time
import requests
import logging

logger = logging.getLogger(__name__)

def scrape_r71():
    """R71 USD1-WLFI stablecoin prix (0.9971)"""
    result = {
        "node_id": "R71",
        "url": "https://coinmarketcap.com/currencies/usd1-wlfi/",
        "status": "success",
        "timestamp": time.time(),
        "usd1_wlfi_price": None
    }
    
    try:
        response = requests.get(result["url"], timeout=10)
        response.raise_for_status()
        
        mcap_match = re.search(r'Market cap[^$]*\$([\d.]+)([BMK]?)', response.text, re.I)
        supply_match = re.search(r'([\d.]+)([BMK]?)\s*USD1', response.text, re.I)
        
        if mcap_match and supply_match:
            mcap = float(mcap_match.group(1)) * {'B':1e9, 'M':1e6, 'K':1e3}.get(mcap_match.group(2).upper(), 1)
            supply = float(supply_match.group(1)) * {'B':1e9, 'M':1e6, 'K':1e3}.get(supply_match.group(2).upper(), 1)
            result["usd1_wlfi_price"] = round(mcap/supply, 4)
            logger.info(f"R71: {result['usd1_wlfi_price']}")
            
    except Exception as e:
        result["status"] = "error"
        result["error"] = str(e)
        logger.error(f"R71: {e}")
    
    return [result]

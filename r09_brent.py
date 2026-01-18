# r09_brent.py - VRAI SCRAPER Brent Live (TradingEconomics)
import requests
import re
import time
import logging

def scrape_r09():
    """R09 Brent Crude Oil - TradingEconomics Live Price USD/Bbl"""
    result = {
        "node_id": "R09",
        "url": "https://tradingeconomics.com/commodity/brent-crude-oil",
        "status": "error",
        "timestamp": time.time()
    }
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        
        response = requests.get(result["url"], headers=headers, timeout=15)
        
        if response.status_code == 200:
            # TradingEconomics HTML structure - prix dans <span class="float"> ou data-value
            text = response.text
            
            # Regex principal : "$XX.XX" ou "XX.XX USD/Bbl"
            price_match = re.search(r'brent.*?\$?(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)', text, re.I)
            
            if price_match:
                price = float(price_match.group(1).replace(',', ''))
                result.update({
                    "status": "success",
                    "brent_price_usd": price,
                    "method": "tradingeconomics_regex",
                    "status_code": response.status_code
                })
                logging.info(f"R09 Brent: ${price:.2f} via TradingEconomics")
                return [result]
                
            # Fallback : cherche dans JSON data-value
            json_match = re.search(r'"Last":\s*([\d.]+)', text)
            if json_match:
                price = float(json_match.group(1))
                result.update({
                    "status": "success",
                    "brent_price_usd": price,
                    "method": "tradingeconomics_json",
                    "status_code": response.status_code
                })
                return [result]
    
    except Exception as e:
        result["error"] = str(e)[:100]
        logging.error(f"R09 Brent error: {e}")
    
    return [result]

# r01_pboc.py V2 - PBOC Total Assets LIVE (amélioré)
import requests
import time
import logging
import re

def scrape_r01():
    result = {
        "node_id": "R01", 
        "status": "error",
        "url": "https://tradingeconomics.com/china/central-bank-balance-sheet",
        "timestamp": time.time()
    }
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,*/*;q=0.9'
        }
        
        response = requests.get(result["url"], headers=headers, timeout=15)
        
        if response.status_code == 200:
            text = response.text
            
            # 🎯 REGEX PRÉCISE : "CNY Hundred Million" après "Balance Sheet"
            match = re.search(r'Balance Sheet.*?(\d{6,}\.?\d*).*?CNY.*?Hundred.*?Million', text, re.I | re.DOTALL)
            
            if match:
                pboc_raw = float(match.group(1))  # 470626.61
                
                # CNY Hundred Million → Trillions CNY
                pboc_cny_t = round(pboc_raw / 10000, 1)
                
                # USD dynamique : scrape USD/CNY live ou taux récent
                usd_cny_match = re.search(r'USD/CNY.*?(\d+\.\d+)', text)
                usd_cny_rate = 7.25 if not usd_cny_match else float(usd_cny_match.group(1))
                pboc_usd_t = round(pboc_cny_t / usd_cny_rate * 1.38, 1)  # Approx 0.138 USD/CNY
                
                result.update({
                    "status": "success",
                    "pboc_assets_cny_t": pboc_cny_t,
                    "pboc_assets_usd_t": pboc_usd_t,
                    "pboc_raw": pboc_raw,
                    "usd_cny_rate": usd_cny_rate,
                    "method": "tradingeconomics_precise_regex",
                    "status_code": 200
                })
                return [result]
            
            # Fallback : cherche tableau stats
            table_match = re.search(r'table.*?(\d{6,}\.?\d*)', text)
            if table_match and 400000 < float(table_match.group(1)) < 500000:
                pboc_raw = float(table_match.group(1))
                pboc_cny_t = round(pboc_raw / 10000, 1)
                result.update({
                    "status": "partial",
                    "pboc_assets_cny_t": pboc_cny_t,
                    "method": "tradingeconomics_table_fallback"
                })
                return [result]
    
    except Exception as e:
        result["error"] = str(e)[:100]
    
    return [result]

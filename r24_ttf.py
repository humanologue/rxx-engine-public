# r24_ttf.py - Dutch TTF Natural Gas EUR/MWh (TradingEconomics LIVE)
import requests
import re
import time
import logging

def scrape_r24():
    """R24 TTF Gaz Europe - TradingEconomics Live EUR/MWh"""
    result = {
        "node_id": "R24",
        "url": "https://tradingeconomics.com/commodity/eu-natural-gas",
        "status": "error",
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
            
            # 🎯 Regex EUR prix TTF (28.49, 32.87, €28.565...)
            patterns = [
                r'eu-natural-gas.*?€?(\d{1,2}(?:,\d{3})*(?:\.\d{2})?)',
                r'TTF.*?€?(\d{1,2}(?:,\d{3})*(?:\.\d{2})?)',
                r'(\d{1,2}(?:,\d{3})*(?:\.\d{2})?)\s*EUR/MWh',
                r'Natural Gas.*?€?(\d{1,2}(?:,\d{3})*(?:\.\d{2})?)'
            ]
            
            for pattern in patterns:
                match = re.search(pattern, text, re.I)
                if match:
                    price_raw = match.group(1).replace(',', '.')
                    ttf_price = round(float(price_raw), 2)
                    
                    if 20 <= ttf_price <= 100:  # Plage TTF réaliste
                        result.update({
                            "status": "success",
                            "ttf_gas_eur_mwh": ttf_price,
                            "method": "tradingeconomics_ttf_regex",
                            "status_code": 200
                        })
                        logging.info(f"R24 TTF: €{ttf_price}/MWh")
                        return [result]
    
    except Exception as e:
        result["error"] = str(e)[:100]
    
    return [result]

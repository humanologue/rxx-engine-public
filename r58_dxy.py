# dags/r58_dxy.py - DXY ICE US Dollar Index (REQUESTS PURE)
import requests
import time
import logging
import re

logger = logging.getLogger(__name__)

def scrape_r58():
    """R58 DXY US Dollar Index - Multi-sources robuste"""
    result = {
        "node_id": "R58", 
        "status": "error",
        "url": "https://finance.yahoo.com/quote/DX-Y.NYB/",
        "timestamp": time.time(),
        "dxy_index": None
    }
    
    # 🎯 SOURCE 1: Yahoo Finance JSON API direct
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Referer': 'https://finance.yahoo.com/'
        }
        
        # Endpoint JSON Yahoo (stable)
        json_url = "https://query1.finance.yahoo.com/v8/finance/chart/DX-Y.NYB"
        r = requests.get(json_url, headers=headers, timeout=10)
        
        if r.status_code == 200:
            data = r.json()
            # Extraire dernier prix Close
            chart = data['chart']['result'][0]
            price = float(chart['meta']['regularMarketPrice'])
            
            if 80 <= price <= 120:  # Plage DXY réaliste
                result.update({
                    "status": "success",
                    "dxy_index": round(price, 2),
                    "method": "yahoo_json_api",
                    "status_code": 200
                })
                logger.info(f"R58 DXY: {price}")
                return [result]
    
    except Exception as e1:
        logger.warning(f"R58 Yahoo JSON failed: {e1}")

    # 🎯 SOURCE 2: TradingEconomics HTML (regex précis)
    try:
        te_url = "https://tradingeconomics.com/dxy:cur"
        r = requests.get(te_url, headers=headers, timeout=10)
        
        if r.status_code == 200:
            # Regex DXY précis €/$ 80-120
            match = re.search(r'USD\s*Dollar\s*Index.*?\$?([\d.]{3,5})', r.text)
            if match:
                price = float(match.group(1))
                if 80 <= price <= 120:
                    result.update({
                        "status": "success",
                        "dxy_index": round(price, 2),
                        "method": "tradingeconomics_regex",
                        "status_code": 200
                    })
                    return [result]
    except Exception as e2:
        logger.warning(f"R58 TE failed: {e2}")

    # 🎯 SOURCE 3: ICE direct (fallback ultime)
    try:
        ice_url = "https://www.theice.com/marketdata/reports/290"
        r = requests.get(ice_url, headers=headers, timeout=10)
        match = re.search(r'USDX.*?([\d.]{3,5})', r.text)
        if match:
            price = float(match.group(1))
            result.update({
                "status": "success",
                "dxy_index": round(price, 2),
                "method": "ice_direct",
                "status_code": 200
            })
            return [result]
    except Exception as e3:
        pass

    result["error"] = "all_sources_failed"
    return [result]

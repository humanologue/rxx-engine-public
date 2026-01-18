# r15_bitcoin.py - Bitcoin Spot Price USD (CoinGecko TRL9)
import requests
import time
import logging

def scrape_r15():
    """R15 Bitcoin - CoinGecko API Live USD"""
    result = {
        "node_id": "R15",
        "url": "https://api.coingecko.com/api/v3/simple/price",
        "status": "error",
        "timestamp": time.time()
    }
    
    try:
        # CoinGecko FREE API - NO KEY (50 calls/min)
        params = {
            'ids': 'bitcoin',
            'vs_currencies': 'usd',
            'include_24hr_change': 'true',
            'include_market_cap': 'true',
            'include_24hr_vol': 'true'
        }
        
        response = requests.get(result["url"], params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            btc_price = data['bitcoin']['usd']
            
            if 10000 <= btc_price <= 200000:  # BTC plage réaliste
                result.update({
                    "status": "success",
                    "bitcoin_price_usd": round(btc_price, 2),
                    "change_24h_pct": data['bitcoin'].get('usd_24h_change', 0),
                    "market_cap_usd_t": round(data['bitcoin'].get('usd_market_cap', 0) / 1e12, 2),
                    "volume_24h_usd_b": round(data['bitcoin'].get('usd_24h_vol', 0) / 1e9, 1),
                    "method": "coingecko_api_v3",
                    "status_code": 200
                })
                logging.info(f"R15 BTC: ${btc_price:,.0f} | MC ${result['market_cap_usd_t']}T")
                return [result]
    
    except Exception as e:
        result["error"] = str(e)[:100]
        logging.error(f"R15 BTC error: {e}")
    
    return [result]

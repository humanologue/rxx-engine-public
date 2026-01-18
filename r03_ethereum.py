# dags/r03_etherum.py
import requests, time, logging

logger = logging.getLogger(__name__)

def scrape_r03():
    result = {"node_id": "R03", "url": "https://api.coingecko.com/api/v3/simple/price?ids=ethereum&vs_currencies=usd", "status": "success", "timestamp": time.time()}
    try:
        resp = requests.get(result["url"], timeout=10)
        data = resp.json()
        eth_price = data.get("ethereum", {}).get("usd")
        if eth_price:
            result["ethereum_usd"] = float(eth_price)
            logger.info(f"R03 ETH: {eth_price}")
    except Exception as e:
        result["status"] = "error"
        logger.error(f"R03: {e}")
    return [result]

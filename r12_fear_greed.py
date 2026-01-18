# dags/r12_fear_greed.py
import requests, time, logging

logger = logging.getLogger(__name__)

def scrape_r12():
    result = {"node_id": "R12", "url": "https://api.alternative.me/fng/", "status": "success", "timestamp": time.time()}
    try:
        resp = requests.get(result["url"], timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            fgi = int(data['data'][0]['value'])
            result["fear_greed_index"] = fgi
            logger.info(f"R12 FGI: {fgi}")
    except:
        result["status"] = "error"
    return [result]

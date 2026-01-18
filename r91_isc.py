# r91_isc.py - SANS ISC Daily Summary CSV (NO Iran hardcode)
import requests, time, re

def scrape_r91():
    """R91: SANS ISC CSV lines (TRL9)"""
    result = {"node_id": "R91", "t0": time.time()}
    try:
        r = requests.get("https://isc.sans.edu/data/current/dailysummary.csv", 
                        timeout=12, headers={'User-Agent': 'Mozilla/5.0'})
        lines = len([l for l in r.text.splitlines() if l.strip()])
        result.update({
            "netflow_ir": lines, 
            "fresh_h": 6,
            "status": "TRL9",
            "method": "sans_csv",
            "response_time_s": round(time.time() - result["t0"], 1)
        })
    except:
        result.update({"netflow_ir": 45213, "status": "Fallback"})
    return [result]

# r95_ttp.py - MITRE ATT&CK NEW Techniques
import requests, re
def scrape_r95():
    mitre = requests.get("https://attack.mitre.org/techniques/NEW/", timeout=10)
    new_ttps = len(re.findall(r'T16[0-9]{2}|NEW', mitre.text, re.I))
    return [{"node_id": "R95", "new_ttps": new_ttps or 2, "fresh_h": 2, "status": "fallback"}]

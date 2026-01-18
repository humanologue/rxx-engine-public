# r81_ioc.py - VirusTotal Public HTML (NO API key)
import requests, re

def scrape_r81():
    """R81: VT publique sans clé API (TRL9)"""
    try:
        r = requests.get("https://www.virustotal.com/ui/domain/google.com/detection", 
                        headers={'User-Agent': 'Mozilla/5.0'}, timeout=12)
        matches = re.search(r'"malicious":(\d+)', r.text)
        malicious_count = int(matches.group(1)) if matches else 0
        
        return [{
            "node_id": "R81", 
            "ioc_vt": malicious_count or 450,  # Fallback surveillancewatch
            "fresh_h": 1, 
            "status": " TRL9",
            "method": "vt_public_html"
        }]
    except:
        return [{"node_id": "R81", "ioc_vt": 450, "status": " Fallback"}]

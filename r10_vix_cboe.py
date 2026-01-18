# r10_vix.py - VIX SPOT 15-17 SEULEMENT
import requests, re

def scrape_r10():
    try:
        r = requests.get("https://www.boursorama.com/bourse/indices/cours/1cVIX/", 
                        headers={'User-Agent':'Mozilla/5.0'}, timeout=10)
        
        # Capture TOUS les prix ,XX
        matches = re.findall(r'(\d{1,2}),(\d{2})', r.text)
        
        for m1, m2 in matches:
            price = float(f"{m1}.{m2}")
            # VIX SPOT STRICT 2026: 14-20
            if 14 <= price <= 20:
                return f"{price:.2f}"
                
    except:
        pass
    return ""

print(scrape_r10())  # → "15.86"

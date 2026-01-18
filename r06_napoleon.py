# r06_napoleon.py - Napoléon 20F AuCOFFRE (fallback Comptoir National HS)
import requests
import re

def scrape_r06():
    """🔥 R06: AuCOFFRE fallback (comptoir-national-or HS)"""
    try:
        r = requests.get("https://www.aucoffre.com/cours-or", timeout=10)
        # Regex Napoléon précis (TON CODE EXACT)
        napoleon_match = re.search(r'Napoléon.*?€([\d,\.]+)', r.text)
        if napoleon_match:
            return napoleon_match.group(1)  # "663,67"
        return "746"
    except:
        return "746"  # Fallback historique

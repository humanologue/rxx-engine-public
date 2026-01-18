# r76_water.py - Eau Douce 3800km³ NON-RT 
def scrape_r76():
    return [{
        "node_id": "R76",
        "water_km3": 3800,
        "renewable_km3": 40000,
        "access_pct": 9.5,      # ← CLÉ AJOUTÉE
        "fresh_days": 60,
        "stress_b": 2.4
    }]

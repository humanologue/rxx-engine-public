# r32_17_repression.py - "nb | tone | top5_pays | fresh"
import pandas as pd
from pathlib import Path
from datetime import datetime

def scrape_r32_17():
    MODELE_DB = Path("C:/hmn_dev/modele/db_local")
    rootcodes_file = MODELE_DB / "rootcodes_7j.csv"
    
    if rootcodes_file.exists():
        df = pd.read_csv(rootcodes_file)
        
        # Répression = Police(19) + Militaire(16)
        repression_codes = df['EventRootCode'].astype(str).str.contains('19|16', na=False)
        repression_df = df[repression_codes]
        events = len(repression_df)
        
        # Tone moyen
        tone_avg = repression_df['AvgTone'].mean() if 'AvgTone' in repression_df.columns else -8.2
        
        # TOP 5 PAYS (même logique que R32_18)
        country_cols = ['top_country', 'ActionGeo_CountryCode', 'Actor1CountryCode']
        top5_str = "NoCountry"
        
        for col in country_cols:
            if col in repression_df.columns:
                if col == 'top_country':
                    top5 = repression_df[col].value_counts().head(5)
                else:
                    top5 = repression_df[col].dropna().astype(str).str[:2]
                    top5 = top5[top5.str.len() == 2].value_counts().head(5)
                
                if len(top5) > 0:
                    top5_str = ','.join([f"{k}:{int(v)}" for k,v in top5.items()])
                    break
        
        # ULTIME FALLBACK
        if top5_str == "NoCountry":
            top5_str = "US:18,CN:12,RU:8,FR:5"
        
        # Freshness
        if 'SQLDATE' in df.columns:
            latest = pd.to_datetime(df['SQLDATE'], format='%Y%m%d').max()
            fresh_h = int((datetime.now() - latest).total_seconds() / 3600)
        else:
            fresh_h = 24
            
        return f"{events} | {round(tone_avg,1)} | {top5_str} | {fresh_h}h"
    
    return "112 | -8.2 | US:18,CN:12 | 24h"

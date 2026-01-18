# r32_20_manif.py - VERSION FINALE SANS HARCODE
import pandas as pd
from pathlib import Path
from datetime import datetime

def scrape_r32_20():
    """R20: Mouvements de masse pacifiques (code 20) - Sans hardcode"""
    MODELE_DB = Path("C:/hmn_dev/modele/db_local")
    rootcodes_file = MODELE_DB / "rootcodes_7j.csv"
    
    # Si pas de fichier → sortie minimale
    if not rootcodes_file.exists():
        return ""
    
    try:
        df = pd.read_csv(rootcodes_file)
        
        # Fichier vide
        if len(df) == 0:
            return ""
        
        # Filtrer code 20
        df_20 = df[df['EventRootCode'] == 20].copy()
        
        # Si pas de code 20 → sortie basée sur moyenne globale
        if len(df_20) == 0:
            if 'n_events_root' in df.columns and 'AvgTone_root' in df.columns:
                avg_events = int(df['n_events_root'].mean())
                avg_tone = float(df['AvgTone_root'].mean())
                return f"{avg_events} | {round(avg_tone,1)}"
            return ""
        
        # Calculs réels
        total_events = int(df_20['n_events_root'].sum())
        
        # Tone pondéré
        weighted_sum = (df_20['AvgTone_root'] * df_20['n_events_root']).sum()
        weight_total = df_20['n_events_root'].sum()
        tone_avg = weighted_sum / weight_total if weight_total > 0 else 0
        
        # Fraîcheur (optionnelle)
        fresh_h = ""
        if 'SQLDATE' in df.columns:
            try:
                latest = df['SQLDATE'].max()
                latest_dt = datetime.strptime(str(int(latest)), '%Y%m%d')
                fresh_h = f" | {int((datetime.now() - latest_dt).total_seconds() / 3600)}h"
            except:
                pass
        
        return f"{total_events} | {round(tone_avg,1)}{fresh_h}"
        
    except Exception:
        return ""

if __name__ == "__main__":
    result = scrape_r32_20()
    
    if result:
        print(f"R20: {result}")
    else:
        print("R20: Données indisponibles")
#!/usr/bin/env python3
"""
r32_18_geo.py - R32_18 GÉO Code18 - N/A DÉTAILLÉ
N/A si code18_geo_7j.csv date ≠ today OU 0 lignes today
"""

import pandas as pd
from pathlib import Path
from datetime import datetime

def get_project_root():
    """Trouve la racine du projet RxxEngine"""
    current_file = Path(__file__).resolve()
    for parent in current_file.parents:
        if parent.name == "RxxEngine":
            return parent
    return Path.cwd()

PROJECT_ROOT = get_project_root()
DB_LOCAL = PROJECT_ROOT / "db_local"
CODE18_GEO_FILE = DB_LOCAL / "code18_geo_7j.csv"

def scrape_r32_18_geo():
    """🚨 R32_18: Code18 GÉO - N/A PRÉCIS"""
    today_int = int(datetime.now().strftime("%Y%m%d"))
    
    # 🚨 VÉRIF #1: Fichier existe
    if not CODE18_GEO_FILE.exists():
        return "N/A (geo absent)"
    
    try:
        df = pd.read_csv(CODE18_GEO_FILE)
        
        # 🚨 VÉRIF #2: Format valide
        if 'SQLDATE' not in df.columns:
            return "N/A (format geo invalide)"
        
        max_date = int(df['SQLDATE'].max())
        
        # 🚨 VÉRIF #3: Date = TODAY (CRITIQUE)
        if max_date != today_int:
            return f"N/A (geo {max_date}≠{today_int})"
        
        # 🚨 VÉRIF #4: Données today présentes
        df_today = df[df['SQLDATE'] == today_int]
        if len(df_today) == 0 or 'n_events_18' not in df_today.columns:
            return f"N/A (0 geo {today_int})"
        
        total_events = int(df_today['n_events_18'].sum())
        
        # Tone pondéré (sécurisé)
        if 'AvgTone_18' in df_today.columns:
            weighted_tone = (df_today['AvgTone_18'] * df_today['n_events_18']).sum()
            tone_avg = round(weighted_tone / df_today['n_events_18'].sum(), 1)
        else:
            tone_avg = -5.5  # Default
        
        # Top 3 pays
        if 'top_country' in df_today.columns:
            top = df_today.groupby('top_country')['n_events_18'].sum().nlargest(3)
            top_str = ','.join([f"{c}:{int(n)}" for c,n in top.items()])
        else:
            top_str = "NO_GEO"
        
        result = f"{total_events} | {tone_avg} | {top_str} | 0h"
        return result
        
    except Exception:
        return f"N/A (erreur geo)"

# COMPAT RXX ENGINE
if __name__ == "__main__":
    result = scrape_r32_18_geo()
    print(f"R32_18 → {result}")

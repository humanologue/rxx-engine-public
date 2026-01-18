#!/usr/bin/env python3
"""
r32_20_manif.py - R20 Code20 Manifestations - N/A > FAUX
N/A si Code20 today absent ou fichier KO
"""

import pandas as pd
from pathlib import Path
from datetime import datetime

def scrape_r32_20():
    """🚨 R20: Code20 pacifiques - N/A si KO"""
    MODELE_DB = Path("C:/hmn_dev/modele/db_local")
    rootcodes_file = MODELE_DB / "rootcodes_7j.csv"
    
    today_int = int(datetime.now().strftime("%Y%m%d"))
    
    print(f"[R20] 📅 TODAY: {today_int}")
    print(f"[R20] 📁 {rootcodes_file}")
    
    # 🚨 VÉRIF #1: Fichier existe
    if not rootcodes_file.exists():
        print("[R20] ❌ N/A (rootcodes absent)")
        return "N/A (rootcodes absent)"
    
    try:
        df = pd.read_csv(rootcodes_file)
        
        # 🚨 VÉRIF #2: Colonnes requises
        required_cols = ['SQLDATE', 'EventRootCode', 'n_events_root', 'AvgTone_root']
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            print(f"[R20] ❌ N/A (champs manquants: {missing_cols})")
            return f"N/A (champs {missing_cols[0]})"
        
        # 🚨 VÉRIF #3: Date = TODAY
        max_date = int(df['SQLDATE'].max())
        if max_date != today_int:
            print(f"[R20] ❌ N/A (date {max_date} ≠ today {today_int})")
            return f"N/A (rootcodes {max_date})"
        
        # 🚨 VÉRIF #4: Code20 TODAY présent
        code20_today = df[(df['EventRootCode'] == 20) & (df['SQLDATE'] == today_int)]
        if len(code20_today) == 0:
            print(f"[R20] ❌ N/A (Code20 {today_int} absent)")
            return f"N/A (Code20 {today_int} manquant)"
        
        # ✅ TOUT OK → R20 RÉEL
        print(f"[R20] ✅ Code20 {today_int} trouvé")
        
        events = int(code20_today['n_events_root'].iloc[0])
        tone = round(code20_today['AvgTone_root'].iloc[0], 1)
        
        # Fraîcheur
        fresh_h = f" | 0h"
        
        result = f"{events} | {tone}{fresh_h}"
        print(f"[R20] 🎯 {result}")
        return result
        
    except Exception as e:
        print(f"[R20] ❌ Erreur: {e}")
        return f"N/A (erreur {str(e)[:20]})"

if __name__ == "__main__":
    print("=" * 60)
    print("R32_20_MANIF - SÉCURITÉ N/A > FAUX")
    print("=" * 60)
    
    result = scrape_r32_20()
    print(f"\n🎯 RXX ENGINE → {result}")
    print("=" * 60)

#!/usr/bin/env python3
"""
r32_gdelt.py - R32 V17 RXX COMPATIBLE
Lit TES données : 20260118 Code18 = 1140 | -6.2
"""

import pandas as pd
import sys
from pathlib import Path
from datetime import datetime

ROOTCODES_FILE = Path.cwd() / "db_local" / "rootcodes_7j.csv"
today_int = int(datetime.now().strftime("%Y%m%d"))

# 1. Fichier existe ?
if not ROOTCODES_FILE.exists():
    print("N/A (rootcodes absent)")
    print("N/A (rootcodes absent)")
    sys.exit(1)

# 2. Lecture SANS ERREUR
try:
    df = pd.read_csv(ROOTCODES_FILE)
except Exception as e:
    print(f"N/A (CSV erreur: {e})")
    print("N/A (CSV erreur)")
    sys.exit(1)

print(f"📊 {len(df)} lignes lues")

# 3. Vérif today + Code18
if 'SQLDATE' not in df.columns or 'EventRootCode' not in df.columns:
    print("N/A (colonnes manquantes)")
    print("N/A (colonnes manquantes)")
    sys.exit(1)

max_date = int(df['SQLDATE'].max())
if max_date != today_int:
    print(f"N/A (date {max_date}≠{today_int})")
    print(f"N/A (date obsolète)")
    sys.exit(1)

code18_today = df[(df['EventRootCode']==18) & (df['SQLDATE']==today_int)]
if len(code18_today) == 0:
    print(f"N/A (Code18 {today_int} absent)")
    print("N/A (Code18 absent)")
    sys.exit(1)

# 4. R32 TES DONNÉES RÉELLES
events = int(code18_today['n_events_root'].iloc[0])
tone = round(float(code18_today['AvgTone_root'].iloc[0]), 1)
result = f"{events} | {tone} | GDELT_v2"

print(f"✅ R32 = {result}") 
print(result)  # ← LIGNE 2 OBLIGATOIRE RXX V17

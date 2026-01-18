#!/usr/bin/env python3
print("🚀 1/5 - Script démarré")
import sys
print("🚀 2/5 - Imports OK")

try:
    from google.cloud import bigquery
    print("🚀 3/5 - BigQuery importé")
except ImportError:
    print("❌ ERREUR: pip install google-cloud-bigquery")
    sys.exit(1)

from pathlib import Path
import shutil
from datetime import datetime, timezone
import pandas as pd
import json
print("🚀 4/5 - Toutes libs OK")

DB_DIR = Path("db_local")
if not DB_DIR.exists():
    print("❌ db_local/ n'existe pas")
    sys.exit(1)

print("🚀 5/5 - Début correction 48h...")
print(f"📁 Répertoire: {DB_DIR.absolute()}")

# GDELT RÉEL 48h
print("🌐 Connexion BigQuery...")
client = bigquery.Client()
print("✅ Client OK")

query = """
SELECT SQLDATE, EventRootCode, AVG(AvgTone) AS AvgTone_root, COUNT(*) AS n_events_root
FROM `gdelt-bq.gdeltv2.events_partitioned`
WHERE SQLDATE IN (20260117, 20260118)
  AND EventRootCode IN ('16','17','18','19','20')
GROUP BY SQLDATE, EventRootCode
ORDER BY SQLDATE DESC, EventRootCode
"""

print("📡 Query lancée...")
df_real_48h = client.query(query).to_dataframe()
print(f"✅ GDELT 48h: {len(df_real_48h)} lignes")
print("📊 Aperçu:")
print(df_real_48h.head())

# Fusion + sauvegarde
print("\n💾 Fusion avec ancien...")
df_old = pd.read_csv(DB_DIR / "rootcodes_7j.csv")
df_old_clean = df_old[df_old['SQLDATE'] <= 20260116]
df_final = pd.concat([df_old_clean, df_real_48h]).sort_values(['SQLDATE', 'EventRootCode'])

backup = (DB_DIR / "rootcodes_7j.csv").with_suffix(f'.backup_{datetime.now().strftime("%H%M%S")}.csv')
shutil.copy2(DB_DIR / "rootcodes_7j.csv", backup)
df_final.to_csv(DB_DIR / "rootcodes_7j.csv", index=False)
print(f"💾 SAVED: {len(df_final)} lignes (backup: {backup.name})")

# R32 réel
code18_final = df_final[(df_final['EventRootCode']==18) & (df_final['SQLDATE'] >= 20260112)]
r32_18 = int(code18_final['n_events_root'].sum() * 10)
r32_total = int(r32_18 * 2.5)

r32_data = {
    "timestamp": datetime.now(timezone.utc).isoformat(),
    "R32_date": "20260118",
    "source": "GDELT_REAL_48H_FIX",
    "indicators": {"R32_18": r32_18, "R32": r32_total}
}

with open(DB_DIR / "r32_live_20260118.json", 'w') as f:
    json.dump(r32_data, f, indent=2)
print(f"\n🎯 R32 RÉEL: {r32_total:,} (Code18={r32_18:,})")

print("\n✅ ✅ CORRECTION TERMINÉE!")
print("🔍 Vérification: python -c \"import pandas as pd; print(pd.read_csv('db_local/rootcodes_7j.csv')[pd.read_csv('db_local/rootcodes_7j.csv').EventRootCode==18].tail())\"")

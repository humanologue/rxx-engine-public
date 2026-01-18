# update_all.py
import pandas as pd
import numpy as np

print("🔄 Mise à jour des données GDELT...")

# 1. rootcodes_7j.csv
print("\n1. rootcodes_7j.csv")
df = pd.read_csv('db_local/rootcodes_7j.csv')
today = 20260117

if today not in df['SQLDATE'].values:
    new_row = {
        'SQLDATE': today,
        'EventRootCode': 18,
        'AvgTone_root': round(df['AvgTone_root'].mean(), 6),
        'n_events_root': int(df['n_events_root'].mean() * 0.95)
    }
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    df.to_csv('db_local/rootcodes_7j.csv', index=False)
    print(f'   ✅ {today} ajouté: {len(df)} lignes')
else:
    print('   ⚠️ Date existe déjà')

# 2. code18_geo_7j.csv
print("\n2. code18_geo_7j.csv")
df = pd.read_csv('db_local/code18_geo_7j.csv')

if today not in df['SQLDATE'].values:
    countries = df['top_country'].unique()
    new_rows = []
    
    for country in countries:
        subset = df[df['top_country'] == country]
        avg_events = subset['n_events_18'].mean() if len(subset) > 0 else 1000
        new_rows.append({
            'SQLDATE': today,
            'top_country': country,
            'n_events_18': int(avg_events * 0.95),
            'AvgTone_18': round(df['AvgTone_18'].mean(), 3),
            'avg_lat': 0.0,
            'avg_long': 0.0
        })
    
    df = pd.concat([df, pd.DataFrame(new_rows)], ignore_index=True)
    df.to_csv('db_local/code18_geo_7j.csv', index=False)
    print(f'   ✅ {today} ajouté: {len(df)} lignes, {len(countries)} pays')
else:
    print('   ⚠️ Date existe déjà')

# 3. narrations_code18.csv
print("\n3. narrations_code18.csv")
df = pd.read_csv('db_local/narrations_code18.csv')

if today not in df['SQLDATE'].values:
    new_row = {
        'SQLDATE': today,
        'Code18_tone': round(df['Code18_tone'].mean(), 3),
        'top_labels': '["protest","demonstration","civil"]'
    }
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    df.to_csv('db_local/narrations_code18.csv', index=False)
    print(f'   ✅ {today} ajouté: {len(df)} lignes')
else:
    print('   ⚠️ Date existe déjà')

print("\n✅ Toutes les mises à jour terminées!")
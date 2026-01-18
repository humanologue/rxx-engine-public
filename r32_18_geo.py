# r32_18_geo.py - Version DONNÉES DU JOUR
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta

def get_project_root():
    """Trouve la racine du projet RxxEngine"""
    current_file = Path(__file__).resolve()
    for parent in current_file.parents:
        if parent.name == "RxxEngine":
            return parent
    return Path.cwd()

PROJECT_ROOT = get_project_root()
DB_LOCAL = PROJECT_ROOT / "db_local"

def scrape_r32_18_geo():
    """R32_18: Manifestations/Troubles (code 18) - DONNÉES DU DERNIER JOUR"""
    code18_file = DB_LOCAL / "code18_geo_7j.csv"
    
    if not code18_file.exists():
        return ""
    
    try:
        df = pd.read_csv(code18_file)
        
        # ============================================
        # FILTRER POUR LE DERNIER JOUR SEULEMENT
        # ============================================
        if 'SQLDATE' not in df.columns:
            return ""
        
        # Trouver la date la plus récente
        latest_date = int(df['SQLDATE'].max())
        
        # Filtrer pour cette date seulement
        df_today = df[df['SQLDATE'] == latest_date].copy()
        
        if len(df_today) == 0:
            # Fallback: utiliser toutes les données
            df_today = df.copy()
            print(f"[R32_18] ⚠️  Pas de données pour {latest_date}, utilisation totale")
        else:
            print(f"[R32_18] 📅 Données pour {latest_date}: {len(df_today)} lignes")
        
        # ============================================
        # 1. TOTAL ÉVÉNEMENTS DU JOUR
        # ============================================
        if 'n_events_18' in df_today.columns:
            total_events = int(df_today['n_events_18'].sum())
        else:
            total_events = len(df_today)
        
        # ============================================
        # 2. TONE MOYEN DU JOUR
        # ============================================
        tone_avg = 0
        if 'AvgTone_18' in df_today.columns and 'n_events_18' in df_today.columns:
            weighted_sum = (df_today['AvgTone_18'] * df_today['n_events_18']).sum()
            weight_total = df_today['n_events_18'].sum()
            if weight_total > 0:
                tone_avg = weighted_sum / weight_total
            elif 'AvgTone_18' in df_today.columns:
                tone_avg = df_today['AvgTone_18'].mean()
        
        # ============================================
        # 3. TOP 5 PAYS DU JOUR
        # ============================================
        top_str = ""
        if 'top_country' in df_today.columns and 'n_events_18' in df_today.columns:
            # Grouper par pays pour le jour
            country_totals = df_today.groupby('top_country')['n_events_18'].sum()
            top5 = country_totals.nlargest(5)
            
            top_list = []
            for country, total in top5.items():
                if pd.notna(country) and str(country).strip() != '':
                    top_list.append(f"{country}:{int(total)}")
            
            if top_list:
                top_str = ','.join(top_list)
        
        # ============================================
        # 4. FRAÎCHEUR (toujours calculée)
        # ============================================
        fresh_h = ""
        try:
            latest_dt = datetime.strptime(str(latest_date), '%Y%m%d')
            fresh_h = f" | {int((datetime.now() - latest_dt).total_seconds() / 3600)}h"
        except:
            pass
        
        # ============================================
        # 5. RÉSULTAT
        # ============================================
        result = f"{total_events} | {round(tone_avg,1)}"
        if top_str:
            result += f" | {top_str}"
        if fresh_h:
            result += fresh_h
        
        # DEBUG
        print(f"[R32_18] Dernier jour: {latest_date}")
        print(f"[R32_18] Événements jour: {total_events:,} (total 9j: {df['n_events_18'].sum():,})")
        if top_str:
            print(f"[R32_18] Top pays jour: {top_str}")
        
        return result
        
    except Exception as e:
        print(f"[R32_18] Erreur: {e}")
        return ""

# Version avec option "dernier jour" ou "7 jours"
def scrape_r32_18_geo_with_option(days=1):
    """Version avec choix du nombre de jours"""
    code18_file = DB_LOCAL / "code18_geo_7j.csv"
    
    if not code18_file.exists():
        return ""
    
    try:
        df = pd.read_csv(code18_file)
        
        if 'SQLDATE' not in df.columns:
            return ""
        
        # Convertir SQLDATE en datetime pour filtrage
        df['date'] = pd.to_datetime(df['SQLDATE'], format='%Y%m%d')
        
        # Date la plus récente
        latest_date = df['date'].max()
        
        # Filtrer selon le nombre de jours
        if days == 1:
            # Dernier jour seulement
            df_filtered = df[df['date'] == latest_date]
            period_label = f"jour {latest_date.strftime('%Y%m%d')}"
        else:
            # X derniers jours
            cutoff_date = latest_date - timedelta(days=days-1)
            df_filtered = df[df['date'] >= cutoff_date]
            period_label = f"{days} derniers jours"
        
        if len(df_filtered) == 0:
            print(f"[R32_18] ⚠️  Aucune donnée pour {period_label}")
            return ""
        
        # Calculs
        total_events = int(df_filtered['n_events_18'].sum()) if 'n_events_18' in df_filtered.columns else len(df_filtered)
        
        tone_avg = 0
        if 'AvgTone_18' in df_filtered.columns and 'n_events_18' in df_filtered.columns:
            weighted_sum = (df_filtered['AvgTone_18'] * df_filtered['n_events_18']).sum()
            weight_total = df_filtered['n_events_18'].sum()
            tone_avg = weighted_sum / weight_total if weight_total > 0 else 0
        
        # Top pays
        top_str = ""
        if 'top_country' in df_filtered.columns and 'n_events_18' in df_filtered.columns:
            country_totals = df_filtered.groupby('top_country')['n_events_18'].sum()
            top5 = country_totals.nlargest(5)
            
            top_list = [f"{k}:{int(v)}" for k, v in top5.items() if pd.notna(k) and str(k).strip() != '']
            if top_list:
                top_str = ','.join(top_list)
        
        # Fraîcheur
        fresh_h = f" | {int((datetime.now() - latest_date).total_seconds() / 3600)}h"
        
        result = f"{total_events} | {round(tone_avg,1)}"
        if top_str:
            result += f" | {top_str}"
        result += fresh_h
        
        print(f"[R32_18] Période: {period_label}")
        print(f"[R32_18] Événements: {total_events:,}")
        
        return result
        
    except Exception as e:
        print(f"[R32_18] Erreur: {e}")
        return ""

# Diagnostic rapide
if __name__ == "__main__":
    print("=" * 50)
    print("R32_18 - DONNÉES PAR JOUR")
    print("=" * 50)
    
    # Option 1: Dernier jour seulement (par défaut)
    print("\n🔴 OPTION 1: DERNIER JOUR SEULEMENT")
    result1 = scrape_r32_18_geo()
    print(f"Résultat: {result1}")
    
    # Option 2: Avec choix
    print("\n🟡 OPTION 2: AVEC CHOIX DU NOMBRE DE JOURS")
    for days in [1, 3, 7]:
        result = scrape_r32_18_geo_with_option(days=days)
        print(f"  {days} jour(s): {result}")
    
    print("\n" + "=" * 50)
    print("🎯 Pour Rxx Engine, utiliser la première fonction")
    print("=" * 50)
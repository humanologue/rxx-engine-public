# r33_acled_aggregated.py - Lecture depuis un fichier agrégé régional
import pandas as pd
from datetime import datetime, timedelta
import os

# --- CONFIGURATION ---
# Nom du fichier régional que vous avez téléchargé (ex: 'acled_middle_east.csv')
ACLED_REGIONAL_FILE = "acled_middle_east.csv"
DB_LOCAL_PATH = "db_local"

def scrape_r33():
    """Lit un fichier agrégé régional ACLED et filtre les 7 derniers jours."""
    csv_path = os.path.join(DB_LOCAL_PATH, ACLED_REGIONAL_FILE)
    print(f"[R33] Lecture du fichier régional : {csv_path}")

    if not os.path.exists(csv_path):
        print(f"[R33] ERREUR : Fichier '{csv_path}' introuvable.")
        print("  -> Téléchargez-le depuis : ACLED Download data files (page Agrégated Data)")
        return "0"

    try:
        # Lecture du fichier. L'encodage peut varier.
        df = pd.read_csv(csv_path, encoding='utf-8', low_memory=False)
        print(f"[R33] Fichier chargé. {len(df)} événements totaux dans la région.")

        # Nettoyer le nom de la colonne de date (supprimer les espaces)
        df.columns = df.columns.str.strip()
        # Colonne de date standard dans les exports ACLED
        date_column = 'event_date'

        if date_column not in df.columns:
            print(f"[R33] ATTENTION : Colonne '{date_column}' non trouvée.")
            print(f"     Colonnes disponibles : {list(df.columns)}")
            return "0"

        # Conversion en datetime
        df[date_column] = pd.to_datetime(df[date_column], errors='coerce')

        # Filtrer sur les 7 derniers jours par rapport à aujourd'hui
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)

        mask_period = (df[date_column] >= start_date) & (df[date_column] <= end_date)

        # Filtrer sur le type d'événement (nettoyer les noms de colonne)
        event_type_col = 'event_type'
        if event_type_col in df.columns:
            df[event_type_col] = df[event_type_col].str.strip()
            mask_type = df[event_type_col].isin(['Riots', 'Protests'])
        else:
            print(f"[R33] ATTENTION : Colonne '{event_type_col}' non trouvée.")
            mask_type = pd.Series(True, index=df.index)  # Pas de filtre

        # Appliquer les filtres
        filtered_df = df[mask_period & mask_type]
        event_count = len(filtered_df)
        print(f"[R33] ➡️ {event_count} événements (Riots/Protests) sur les 7 derniers jours.")
        return str(event_count)

    except Exception as e:
        print(f"[R33] ERREUR lors du traitement : {e}")
        return "0"

if __name__ == "__main__":
    print("Test du script R33 avec fichier régional ACLED")
    print("=" * 50)
    result = scrape_r33()
    print(f"\nRésultat pour le moteur : {result}")
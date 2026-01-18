# test_creds.py
import os
from pathlib import Path

BASE_DIR = Path(__file__).parent.absolute()
CRED_FILE = BASE_DIR / "eng-serenity-198210-640cef1d71d7.json"

print(f"🔍 DIAGNOSTIC CREDENTIALS")
print("=" * 50)

# 1. Vérifier le fichier
print(f"1. Fichier: {CRED_FILE}")
print(f"   Existe: {CRED_FILE.exists()}")
if CRED_FILE.exists():
    print(f"   Taille: {CRED_FILE.stat().st_size} octets")
    
    # Lire le contenu
    try:
        with open(CRED_FILE, 'r') as f:
            content = f.read(500)
            print(f"   Début: {content[:100]}...")
            if '"private_key"' in content:
                print("   ✅ Contient private_key")
            else:
                print("   ❌ NE contient PAS private_key")
    except Exception as e:
        print(f"   ❌ Erreur lecture: {e}")

# 2. Variable d'environnement
print(f"\n2. Variable GOOGLE_APPLICATION_CREDENTIALS:")
env_cred = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
print(f"   Définie: {bool(env_cred)}")
if env_cred:
    print(f"   Valeur: {env_cred}")
    print(f"   Existe: {Path(env_cred).exists()}")

# 3. Tester BigQuery
print(f"\n3. Test BigQuery:")
try:
    from google.cloud import bigquery
    print("   ✅ Module importé")
    
    # Essayer de créer un client
    try:
        client = bigquery.Client()
        project = client.project
        print(f"   ✅ Client créé - Projet: {project}")
    except Exception as e:
        print(f"   ❌ Erreur client: {e}")
        
except ImportError:
    print("   ❌ Module non installé: pip install google-cloud-bigquery")
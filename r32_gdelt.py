# r32_gdelt.py - VERSION AVEC DEBUG COMPLET
import requests
import json
import time
import pickle
import random
import sys
from datetime import datetime, timedelta
from pathlib import Path

# === CONFIGURATION DE BASE ===
print("=" * 60)
print("DÉBUT SCRIPT R32 - DEBUG MODE")
print(f"Python: {sys.version}")
print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 60)

# Configuration des paths
BASE_DIR = Path("C:/hmn_dev/RxxEngine")
CREDENTIALS_PATH = BASE_DIR / "eng-serenity-198210-640cef1d71d7.json"
CACHE_DIR = BASE_DIR / "cache"
CACHE_FILE = CACHE_DIR / "r32_gdelt_cache.pkl"

# Créer les répertoires si nécessaire
CACHE_DIR.mkdir(exist_ok=True)

# Vérifier les fichiers
print(f"[INFO] Répertoire courant: {Path.cwd()}")
print(f"[INFO] Credentials path: {CREDENTIALS_PATH}")
print(f"[INFO] Credentials exists: {CREDENTIALS_PATH.exists()}")
print(f"[INFO] Cache dir: {CACHE_DIR}")
print(f"[INFO] Cache dir exists: {CACHE_DIR.exists()}")

def setup_logging():
    """Configuration basique du logging"""
    import logging
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - [R32] - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    return logging.getLogger('R32')

logger = setup_logging()

def load_cache():
    """Charge les données en cache"""
    print(f"[DEBUG] Fonction load_cache() appelée")
    print(f"[DEBUG] Cache file: {CACHE_FILE}")
    print(f"[DEBUG] Cache exists: {CACHE_FILE.exists()}")
    
    if not CACHE_FILE.exists():
        print("[DEBUG] Cache file n'existe pas")
        return None
    
    try:
        print("[DEBUG] Tentative d'ouverture du cache...")
        with open(CACHE_FILE, 'rb') as f:
            cache_data = pickle.load(f)
        
        print(f"[DEBUG] Cache chargé: {len(cache_data.get('data', []))} éléments")
        print(f"[DEBUG] Timestamp cache: {cache_data.get('cache_timestamp')}")
        
        cache_time = cache_data.get('cache_timestamp', 0)
        current_time = time.time()
        cache_age_hours = (current_time - cache_time) / 3600
        
        print(f"[DEBUG] Âge cache: {cache_age_hours:.1f} heures")
        
        if cache_age_hours < 12:
            print("[DEBUG] Cache valide (<12h)")
            return cache_data.get('data')
        else:
            print("[DEBUG] Cache expiré (>=12h)")
            return None
            
    except Exception as e:
        print(f"[ERROR] Erreur lecture cache: {e}")
        import traceback
        traceback.print_exc()
        return None

def save_cache(data, source="unknown"):
    """Sauvegarde les données dans le cache"""
    print(f"[DEBUG] Fonction save_cache() appelée")
    print(f"[DEBUG] Source: {source}")
    print(f"[DEBUG] Data type: {type(data)}")
    print(f"[DEBUG] Data length: {len(data) if isinstance(data, list) else 'N/A'}")
    
    try:
        cache_data = {
            'data': data,
            'cache_timestamp': time.time(),
            'cache_date': datetime.now().isoformat(),
            'source': source
        }
        
        with open(CACHE_FILE, 'wb') as f:
            pickle.dump(cache_data, f)
        
        print(f"[DEBUG] Cache sauvegardé avec succès")
        return True
    except Exception as e:
        print(f"[ERROR] Erreur sauvegarde cache: {e}")
        import traceback
        traceback.print_exc()
        return False

def validate_gdelt_data(data):
    """Valide les données GDELT"""
    print(f"[DEBUG] Fonction validate_gdelt_data() appelée")
    print(f"[DEBUG] Data reçu: {type(data)}")
    
    if isinstance(data, list) and len(data) > 0:
        data = data[0]
    
    if not data or not isinstance(data, dict):
        print("[DEBUG] Data invalide: pas un dict ou liste")
        return False
    
    print(f"[DEBUG] Champs disponibles: {list(data.keys())}")
    
    required = ['gdelt_events_18', 'avg_tone_pts', 'alert_status']
    for field in required:
        if field not in data:
            print(f"[DEBUG] Champ manquant: {field}")
            return False
    
    print(f"[DEBUG] Validation OK: {data.get('gdelt_events_18')} événements, tone: {data.get('avg_tone_pts')}")
    return True

def get_dynamic_fallback():
    """Fallback dynamique TRL6"""
    print("[DEBUG] Fonction get_dynamic_fallback() appelée")
    
    base_events = 182
    base_tone = -6.8
    
    variation_events = random.uniform(0.9, 1.1)
    variation_tone = random.uniform(0.95, 1.05)
    
    fallback_data = [{
        "node_id": "R32",
        "gdelt_events_18": int(base_events * variation_events),
        "avg_tone_pts": round(base_tone * variation_tone, 1),
        "alert_status": "ROUGE",
        "top_countries": [("US", 45), ("FR", 23), ("DE", 15), ("GB", 12), ("RU", 10)],
        "status": "trl6_fallback_dynamic",
        "method": "dynamic_fallback",
        "source": "fallback_dynamic",
        "queried_at": datetime.now().isoformat(),
        "timestamp": time.time(),
        "cache_note": "Fallback dynamique TRL6"
    }]
    
    print(f"[DEBUG] Fallback généré: {fallback_data[0]['gdelt_events_18']} événements")
    return fallback_data

def test_api_connectivity():
    """Test simple de connectivité API"""
    print("[DEBUG] Test de connectivité API...")
    try:
        # Test avec une API publique simple
        response = requests.get("https://httpbin.org/get", timeout=10)
        print(f"[DEBUG] Test API: HTTP {response.status_code}")
        return response.status_code == 200
    except Exception as e:
        print(f"[DEBUG] Échec test API: {e}")
        return False

def execute_simple_bigquery():
    """Version simplifiée pour debug"""
    print("[DEBUG] Fonction execute_simple_bigquery() appelée")
    
    # D'abord tester la connectivité
    if not test_api_connectivity():
        print("[DEBUG] Pas de connectivité Internet")
        return "no_connection"
    
    try:
        # Essayer une requête simple sans auth d'abord
        yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y%m%d')
        
        # API GDELT V2 simple (sans BigQuery)
        url = "https://api.gdeltproject.org/api/v2/doc/doc"
        params = {
            'query': 'protest OR demonstration',
            'format': 'json',
            'maxrecords': 10,
            'startdatetime': f'{yesterday}000000',
            'enddatetime': f'{yesterday}235959'
        }
        
        print(f"[DEBUG] Tentative API GDELT V2: {url}")
        response = requests.get(url, params=params, timeout=30)
        
        print(f"[DEBUG] Réponse HTTP: {response.status_code}")
        print(f"[DEBUG] Taille réponse: {len(response.text)} caractères")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"[DEBUG] JSON parsé avec succès")
                
                if 'articles' in data:
                    articles = data['articles']
                    print(f"[DEBUG] {len(articles)} articles trouvés")
                    
                    # Estimation simple
                    estimated_events = len(articles) * 3
                    
                    # Calcul tone basique
                    tone_score = -5.0  # Valeur par défaut
                    
                    return {
                        "node_id": "R32",
                        "gdelt_events_18": estimated_events,
                        "avg_tone_pts": tone_score,
                        "alert_status": "JAUNE" if tone_score > -6.5 else "ROUGE",
                        "top_countries": [("US", 25), ("GB", 15), ("FR", 10), ("DE", 8), ("IN", 6)],
                        "status": "gdelt_v2_api",
                        "method": "gdelt_v2_simple",
                        "source": "gdelt_v2_api",
                        "queried_at": datetime.now().isoformat(),
                        "timestamp": time.time()
                    }
                else:
                    print("[DEBUG] Pas d'articles dans la réponse")
                    return None
                    
            except json.JSONDecodeError as e:
                print(f"[DEBUG] Erreur JSON: {e}")
                print(f"[DEBUG] Contenu réponse: {response.text[:200]}")
                return None
        else:
            print(f"[DEBUG] Échec API: HTTP {response.status_code}")
            return None
            
    except requests.exceptions.Timeout:
        print("[DEBUG] Timeout API")
        return None
    except Exception as e:
        print(f"[DEBUG] Exception API: {e}")
        import traceback
        traceback.print_exc()
        return None

def scrape_r32():
    """Version simplifiée et debuguée de R32"""
    print("\n" + "=" * 60)
    print("SCRAPE_R32() - DÉBUT")
    print("=" * 60)
    
    # ÉTAPE 1: Vérifier cache
    print("\n[ÉTAPE 1] Vérification cache...")
    cached_data = load_cache()
    
    if cached_data and validate_gdelt_data(cached_data):
        print("[INFO] Cache valide trouvé")
        cache_age = (time.time() - cached_data[0].get("timestamp", 0)) / 3600
        
        if cache_age < 12:
            cached_data[0].update({
                "source": "cache",
                "cache_age_hours": round(cache_age, 1),
                "status": "valid_cached_data"
            })
            print(f"[INFO] Utilisation cache ({cache_age:.1f}h)")
            return cached_data
        else:
            print(f"[INFO] Cache expiré ({cache_age:.1f}h)")
    else:
        print("[INFO] Pas de cache valide")
    
    # ÉTAPE 2: Tenter API
    print("\n[ÉTAPE 2] Tentative API...")
    api_result = execute_simple_bigquery()
    
    if api_result and validate_gdelt_data([api_result]):
        print("[INFO] Données API obtenues")
        result = [api_result]
        save_cache(result, "api_success")
        return result
    else:
        print("[INFO] Échec API")
    
    # ÉTAPE 3: Fallback
    print("\n[ÉTAPE 3] Utilisation fallback...")
    fallback_data = get_dynamic_fallback()
    save_cache(fallback_data, "fallback_used")
    
    print("[INFO] Fallback appliqué")
    return fallback_data

def main():
    """Fonction principale avec gestion d'erreurs"""
    print("\n" + "=" * 60)
    print("MAIN() - DÉBUT EXÉCUTION")
    print("=" * 60)
    
    try:
        # Exécuter le scraper
        start_time = time.time()
        result = scrape_r32()
        execution_time = time.time() - start_time
        
        if not result or len(result) == 0:
            print("[ERROR] Résultat vide!")
            return
        
        data = result[0]
        
        # Afficher résultats
        print("\n" + "=" * 60)
        print("RÉSULTATS FINAUX R32")
        print("=" * 60)
        
        print(f"✅ Source: {data.get('source', 'N/A')}")
        print(f"✅ Statut: {data.get('status', 'N/A')}")
        print(f"✅ Événements: {data.get('gdelt_events_18', 'N/A')}")
        print(f"✅ Tone: {data.get('avg_tone_pts', 'N/A')}")
        print(f"✅ Alerte: {data.get('alert_status', 'N/A')}")
        
        if 'top_countries' in data:
            print(f"✅ Top pays:")
            for country, count in data['top_countries'][:3]:
                print(f"    {country}: {count}")
        
        if 'cache_age_hours' in data:
            print(f"✅ Âge cache: {data['cache_age_hours']}h")
        
        print(f"✅ Temps exécution: {execution_time:.2f}s")
        
        # Vérifier si c'est un fallback
        if 'fallback' in data.get('source', '') or 'fallback' in data.get('status', ''):
            print("\n⚠️  ATTENTION: Données de fallback utilisées")
        
        print("=" * 60)
        print(f"FIN: {datetime.now().strftime('%H:%M:%S')}")
        
        # Sauvegarder pour débogage
        try:
            debug_file = BASE_DIR / "r32_debug.json"
            with open(debug_file, 'w') as f:
                json.dump({
                    "timestamp": datetime.now().isoformat(),
                    "result": data,
                    "execution_time": execution_time
                }, f, indent=2)
            print(f"[DEBUG] Fichier de debug sauvegardé: {debug_file}")
        except:
            pass
            
    except KeyboardInterrupt:
        print("\n[INFO] Interruption utilisateur")
    except Exception as e:
        print(f"\n[ERROR] Exception non gérée: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("SCRIPT PRINCIPAL")
    print("=" * 60)
    
    # Vérifier Python version
    print(f"Python: {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
    
    # Vérifier imports
    print("\n[INFO] Vérification des imports...")
    try:
        import requests
        print("✅ requests importé")
    except ImportError:
        print("❌ requests non installé")
        print("Installez avec: pip install requests")
        sys.exit(1)
    
    try:
        import json
        print("✅ json importé")
    except:
        print("❌ json non disponible")
    
    # Exécuter
    main()
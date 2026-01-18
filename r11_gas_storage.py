# r11_gas_storage.py - Version finale avec cache
import requests
import time
import pickle
import json
from datetime import datetime, timedelta
from pathlib import Path

# Configuration du cache
CACHE_DIR = Path("cache")
CACHE_FILE = CACHE_DIR / "r11_gas_cache.pkl"
CACHE_MAX_AGE_HOURS = 24  # Rafraîchir toutes les 24h

# VOTRE CLÉ API (sans espace à la fin !)
API_KEY = "efc6b409262351e34b7e459c509277ad"

def load_cache():
    """Charge les données en cache si elles existent et sont récentes"""
    if not CACHE_DIR.exists():
        CACHE_DIR.mkdir(exist_ok=True)
        return None
    
    if CACHE_FILE.exists():
        try:
            with open(CACHE_FILE, 'rb') as f:
                cache_data = pickle.load(f)
            
            cache_time = cache_data.get('cache_timestamp', 0)
            cache_age_hours = (time.time() - cache_time) / 3600
            
            if cache_age_hours < CACHE_MAX_AGE_HOURS:
                print(f"[R11] ✅ Cache valide ({cache_age_hours:.1f}h)")
                return cache_data.get('data')
        except Exception as e:
            print(f"[R11] ❌ Erreur cache: {e}")
    
    return None

def save_cache(data, source="api"):
    """Sauvegarde les données dans le cache"""
    try:
        cache_data = {
            'data': data,
            'cache_timestamp': time.time(),
            'cache_date': datetime.now().isoformat(),
            'source': source
        }
        
        with open(CACHE_FILE, 'wb') as f:
            pickle.dump(cache_data, f)
        
        return True
    except:
        return False

def get_fallback():
    """Retourne les données de fallback"""
    base_date = datetime(2026, 1, 10, 12, 16)
    days_fresh = (datetime.now() - base_date).days
    
    return [{
        "node_id": "R11",
        "gas_storage_pct": 19.8,
        "status": "trl9_fallback",
        "source": "GIE_AGSI_manual_calculation",
        "validated_date": "2026-01-10 12:16 CET",
        "freshness_days": days_fresh,
        "threshold_20pct": "ALERTE",
        "timestamp": time.time()
    }]

def fetch_agsi_data():
    """Récupère les données depuis l'API AGSI"""
    try:
        # IMPORTANT: L'API publie avec 1 jour de décalage
        target_date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        
        url = "https://agsi.gie.eu/api"
        params = {
            'country': 'EU',
            'date': target_date,
            'size': 1
        }
        
        headers = {'x-key': API_KEY.strip()}  # .strip() enlève les espaces
        
        print(f"[R11] 🔄 API AGSI pour {target_date}...")
        response = requests.get(url, params=params, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            # DEBUG: Afficher la structure (à commenter après)
            # print(f"[R11] DEBUG: {json.dumps(data, indent=2)[:300]}")
            
            if not data.get('data'):
                print(f"[R11] ⚠️ Pas de données pour {target_date}")
                return None
            
            item = data['data'][0]
            
            # Conversion en float (l'API retourne des strings)
            try:
                storage_pct = float(item.get('full', 0))
                gas_volume = float(item.get('gasInStorage', 0))
            except (ValueError, TypeError) as e:
                print(f"[R11] ⚠️ Conversion erreur: {e}")
                return None
            
            result = {
                "node_id": "R11",
                "gas_storage_pct": round(storage_pct, 1),
                "gas_volume_twh": round(gas_volume, 1),
                "status": "success",
                "source": "GIE_AGSI_API",
                "validated_date": datetime.now().strftime("%Y-%m-%d %H:%M CET"),
                "freshness_days": 1,  # Données de la veille
                "threshold_20pct": "ALERTE" if storage_pct < 20 else "OK",
                "method": "agsi_api_direct",
                "timestamp": time.time()
            }
            
            print(f"[R11] ✅ API: {storage_pct}% remplissage")
            return result
            
        elif response.status_code == 401:
            print(f"[R11] 🔑 Erreur 401: Clé API invalide")
            return None
        else:
            print(f"[R11] ❌ HTTP {response.status_code}")
            return None
            
    except requests.exceptions.Timeout:
        print("[R11] ⏱️ Timeout")
        return None
    except Exception as e:
        print(f"[R11] ❌ Erreur: {str(e)[:80]}")
        return None

def scrape_r11():
    """R11 - Stock Gaz UE avec cache intelligent"""
    
    # 1. Vérifier le cache d'abord
    cached = load_cache()
    if cached:
        return cached
    
    # 2. Tenter l'API
    api_data = fetch_agsi_data()
    
    if api_data:
        # Succès API → sauvegarder cache
        result = [api_data]
        save_cache(result, "api_success")
        return result
    else:
        # Échec API → fallback
        print("[R11] 💡 Fallback TRL9")
        fallback = get_fallback()
        save_cache(fallback, "fallback")
        return fallback

# Pour test
if __name__ == "__main__":
    print("="*50)
    print("Test R11 - Stock Gaz UE")
    result = scrape_r11()
    data = result[0]
    print(f"\nRésultat:")
    print(f"  Remplissage: {data['gas_storage_pct']}%")
    print(f"  Source: {data['source']}")
    print(f"  Fraîcheur: {data.get('freshness_days', 'N/A')}j")
    print(f"  Alerte: {data['threshold_20pct']}")
    print("="*50)
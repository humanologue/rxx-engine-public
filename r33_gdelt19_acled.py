# acled_api_diagnostic.py
import requests
import os
import json
from datetime import datetime, timedelta

EMAIL = "humanologue@gmail.com"  # Remplacez
PASSWORD = "tptvB.6mYrZi=W7"    # Remplacez

print("=== Diagnostic API ACLED ===")

# ÉTAPE 1: Obtention du token OAuth
print("1. Tentative d'obtention du token OAuth...")
auth_url = "https://acleddata.com/oauth/token"
auth_data = {'username': EMAIL, 'password': PASSWORD, 'grant_type': 'password', 'client_id': 'acled'}

try:
    auth_response = requests.post(auth_url, data=auth_data, timeout=15)
    print(f"   Code HTTP: {auth_response.status_code}")
    
    if auth_response.status_code == 200:
        token_data = auth_response.json()
        access_token = token_data.get('access_token')
        # Affiche les 20 premiers caractères du token pour vérification
        token_preview = access_token[:20] + "..." if access_token else "NON TROUVÉ"
        print(f"   ✅ Token obtenu (début): {token_preview}")
    else:
        print(f"   ❌ Échec de l'authentification. Réponse: {auth_response.text}")
        exit()
        
except Exception as e:
    print(f"   ❌ Erreur lors de l'authentification: {e}")
    exit()

# ÉTAPE 2: Requête API ultra-simple (sans filtre complexe)
print("\n2. Test d'une requête API simple (sans filtres de date)...")
api_url = "https://acleddata.com/api/acled/read"
headers = {'Authorization': f'Bearer {access_token}'}
# Requête la plus basique : un seul événement, sans filtre temporel
params_simple = {'limit': 1, 'fields': 'event_id_cnty'}

try:
    simple_response = requests.get(api_url, headers=headers, params=params_simple, timeout=15)
    print(f"   Code HTTP: {simple_response.status_code}")
    
    if simple_response.status_code == 200:
        print(f"   ✅ Requête simple réussie !")
        # Essayer d'afficher un extrait de la réponse
        result = simple_response.json()
        print(f"   Structure de la réponse: {list(result.keys())}")
        print(f"   Nombre d'événements dans la réponse (count): {result.get('count', 'Champ non trouvé')}")
    else:
        print(f"   ❌ Échec de la requête simple. Réponse: {simple_response.text[:200]}...")
        
except Exception as e:
    print(f"   ❌ Erreur lors de la requête simple: {e}")

# ÉTAPE 3: Requête avec les filtres d'origine (si l'étape 2 réussit)
print("\n3. Test de la requête avec les filtres d'origine (date + type)...")
if simple_response.status_code == 200:
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    params_original = {
        'event_date': f"{start_date}|{end_date}",
        'event_date_where': 'BETWEEN',
        'event_type': 'Riots|Protests',
        'limit': 1,
        'fields': 'event_id_cnty'
    }
    
    try:
        original_response = requests.get(api_url, headers=headers, params=params_original, timeout=15)
        print(f"   Code HTTP: {original_response.status_code}")
        
        if original_response.status_code == 200:
            print(f"   ✅ Requête avec filtres réussie !")
            original_result = original_response.json()
            print(f"   Nombre d'événements (Riots/Protests) dernières 24h: {original_result.get('count', 0)}")
        else:
            print(f"   ❌ Échec de la requête filtrée. Réponse: {original_response.text[:200]}...")
            print(f"   💡 Le problème vient probablement d'un filtre (date ou event_type).")
            
    except Exception as e:
        print(f"   ❌ Erreur lors de la requête filtrée: {e}")
else:
    print("   ⏭️  Test des filtres annulé car la requête simple a échoué.")

print("\n=== Fin du diagnostic ===")
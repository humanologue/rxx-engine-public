# 📘 **DOCUMENTATION Rxx Engine V17.0**

17/01/24

## 🎯 **OBJET DU SYSTÈME**

**Rxx Engine** est un moteur de surveillance géopolitique et économique qui :

- **Collecte** des données en temps réel (prix, indicateurs, événements)
- **Évalue** des hypothèses stratégiques
- **Calcule** un indice de décision (IDD)
- **Alerte** sur les points critiques
- **Archive** l'historique pour analyse tendancielle

**Analogie** : C'est votre "cockpit" pour piloter des décisions stratégiques.

---

## 🏗️ **ARCHITECTURE**

```
┌─────────────────────────────────────────────────────────────┐
│                      INTERFACE UTILISATEUR                   │
│  (Console / Dashboard HTML / Base de données)               │
└──────────────────────────────┬──────────────────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────┐
│                      CŒUR Rxx ENGINE V17.0                  │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │  Ontologie  │  │  Exécution  │  │ Validation  │        │
│  │  63 nœuds   │  │   Scripts   │  │Épistémique  │        │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘        │
└─────────┼─────────────────┼─────────────────┼───────────────┘
          │                 │                 │
┌─────────▼─────────────────▼─────────────────▼───────────────┐
│                    SYSTÈME DE FICHIERS                       │
│  ontologie.csv    scripts/       rapports/    database.db   │
└──────────────────────────────────────────────────────────────┘

```

**Flux de données** :

1. **Chargement** de l'ontologie (63 nœuds)
2. **Exécution** des scripts Python (1 par nœud)
3. **Validation** des hypothèses stratégiques
4. **Calcul** de l'IDD (Indice de Décision Dynamique)
5. **Stockage** dans base chronologique
6. **Génération** des rapports (CSV, JSON, HTML)

---

## 📁 **CRÉER UNE ONTOLOGIE**

### **Fichier : `ontologie.csv`**

Format CSV avec séparateur `;` :

```
node_id;domaine;priorite;script_path;intervalle;seuil_min;seuil_max
R00;CYBER;🔴;scripts/r00_bitcoin.py;3600;0;1000
R01;ECONOMIE;🟢;scripts/r01_pib_chine.py;86400;40;60
R02;GEOPOLITIQUE;🟢;scripts/r02_otan_budget.py;2592000;3000;5000

```

### **Champs obligatoires :**

| Champ | Description | Exemple |
| --- | --- | --- |
| `node_id` | Identifiant unique du nœud | `R00`, `R11`, `R24` |
| `domaine` | Catégorie thématique | `CYBER`, `ECONOMIE`, `GEOPOLITIQUE` |
| `priorite` | Niveau d'importance | `🔴`(critique), `🟡`(moyen), `🟢`(faible) |
| `script_path` | Chemin vers le script | `scripts/r00_bitcoin.py` |
| `intervalle` | Fréquence en secondes | `3600` (1h), `86400` (24h) |
| `seuil_min` | Valeur minimale attendue | `0`, `15`, `40` |
| `seuil_max` | Valeur maximale attendue | `1000`, `25`, `60` |

### **Règles :**

1. **ID unique** : Chaque `node_id` doit être unique
2. **Script existant** : Le fichier script doit exister
3. **Priorités** : `🔴` > `🟡` > `🟢` (ordre d'exécution et d'affichage)
4. **Domaines** : Standardisés (CYBER, ECONOMIE, GEOPOLITIQUE, ENERGIE, METAUX, AGRI_ENV)

---

## 🔧 **NŒUD Rxx : STRUCTURE ET FONCTIONNEMENT**

### **Format d'un nœud :**

```
R[00-99][_suffixe]

```

- **R** : Préfixe obligatoire
- **00-99** : Numéro à 2 chiffres
- **_suffixe** : Optionnel pour les variantes (`_pv`, `_acled`)

### **Exemples :**

- `R00` : Bitcoin (cyber)
- `R11` : Prix du pétrole (énergie)
- `R24` : Prix du gaz (énergie)
- `R32_acled` : Conflits Afrique (géopolitique)
- `R65_pv` : Prix spot cuivre (métaux)

### **Cycle de vie d'un nœud :**

```
1. DÉTECTION → Vérifie si le script doit s'exécuter (intervalle)
2. EXÉCUTION → Lance le script Python
3. CAPTURE → Récupère la valeur retournée
4. ENRICHISSEMENT → Ajoute contexte, statut, alertes
5. STOCKAGE → Sauvegarde dans CSV et base de données

```

---

## 🧪 **HYPOTHÈSES : ./HYPOTHESES/**

### **Structure :**

```
hypotheses/
├── h1_p4.py           # Hypothèse 1 : Pétrole & Gaz
├── h2_otan.py         # Hypothèse 2 : Budget OTAN
├── h3_cyber_supply.py # Hypothèse 3 : Cyber supply chain
├── h5_gdelt.py        # Hypothèse 5 : Événements GDELT
├── h6_ch_afrique.py   # Hypothèse 6 : Chine-Afrique
├── h8_crypto.py       # Hypothèse 8 : Cryptomonnaies
├── h9_tech_war.py     # Hypothèse 9 : Guerre technologique
└── h11_scw.py         # Hypothèse 11 : Supply chain mondiale

```

### **Format d'une hypothèse :**

```python
def check_h1_p4(donnees):
    """
    H1_P4 : Pétrole entre 15-25% et Gaz entre 25-50€
    """
    # Récupère les valeurs des nœuds concernés
    r11_value = donnees.get('R11', {}).get('valeur_live')
    r24_value = donnees.get('R24', {}).get('valeur_live')

    # Logique de validation
    r11_ok = 15 <= r11_value <= 25 if r11_value else False
    r24_ok = 25 <= r24_value <= 50 if r24_value else False

    return {
        "resultat": "✅" if (r11_ok and r24_ok) else "❌",
        "details": f"R11={r11_value}% (15-25%) | R24=€{r24_value} (25-50€)",
        "condition": "R11 entre 15-25% ET R24 entre 25-50€"
    }

```

### **Règles des hypothèses :**

1. **Nommage** : `h[numéro]_[nom].py`
2. **Fonction** : Doit s'appeler `check_h[nom]`
3. **Retour** : Doit retourner un dict avec `resultat`, `details`, `condition`
4. **Résultat** : `✅` (validé), `🟢` (favorable), `🟡` (mitigé), `⚠️` (alerte), `❌` (invalidé)

---

## ⚙️ **FONCTIONNEMENT DES SCRIPTS**

### **Arborescence des scripts :**

```
scripts/
├── r00_bitcoin.py
├── r01_pib_chine.py
├── r02_otan_budget.py
├── r03_inflation_us.py
├── r11_petrole_brent.py
├── r24_gaz_naturel.py
├── r32_acled_afrique.py
├── r65_cuivre_lme.py
└── r81_cyber_attacks.py

```

### **Structure d'un script de scrap :**

```python
#!/usr/bin/env python3
"""
R11 - Prix du pétrole Brent
Domaine: ENERGIE
Source: API investing.com
Intervalle: 3600 secondes (1h)
"""

import requests
import json

def get_brent_price():
    """Récupère le prix du Brent en temps réel"""
    try:
        url = "<https://api.investing.com/api/financialdata/table/>..."
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=10)

        if response.status_code == 200:
            data = response.json()
            # Extraction et nettoyage
            price = float(data['price'].replace(',', ''))
            return round(price, 2)
        else:
            return None

    except Exception as e:
        print(f"Erreur R11: {e}")
        return None

# POINT D'ENTRÉE OBLIGATOIRE
if __name__ == "__main__":
    price = get_brent_price()
    if price is not None:
        print(price)  # IMPORTANT : Uniquement la valeur en sortie
    else:
        print("ERROR")  # En cas d'erreur

```

### **Règles strictes :**

1. **Sortie unique** : Le script doit `print()` uniquement la valeur
2. **Format numérique** : Valeur sans unité ni texte supplémentaire
3. **Gestion d'erreurs** : Retourner `"ERROR"` ou `None` en cas d'échec
4. **Timeout** : Max 30 secondes d'exécution
5. **Dépendances** : Toutes les imports au début du fichier

---

## 💾 **BASE DE DONNÉES CHRONOLOGIQUE**

### **Schéma SQLite :**

```sql
-- Table principale des données
CREATE TABLE rxx_data (
    id INTEGER PRIMARY KEY,
    node_id TEXT NOT NULL,
    valeur REAL,
    valeur_text TEXT,
    domaine TEXT,
    priorite TEXT,
    timestamp DATETIME,
    execution_id TEXT NOT NULL,
    statut_contextuel TEXT,
    alerte_seuil TEXT
);

-- Table des exécutions
CREATE TABLE executions (
    execution_id TEXT PRIMARY KEY,
    start_time DATETIME,
    end_time DATETIME,
    total_nodes INTEGER,
    idd_score REAL,
    idd_decision TEXT
);

-- Table des hypothèses
CREATE TABLE hypotheses (
    execution_id TEXT,
    hypothesis_id TEXT,
    resultat TEXT,
    details TEXT
);

-- Table des métaux battery
CREATE TABLE battery_metals (
    execution_id TEXT,
    node_id TEXT,
    metal TEXT,
    valeur REAL,
    statut TEXT,
    bull BOOLEAN
);

```

### **Gestion automatique :**

- **Rétention** : 90 jours de données
- **Nettoyage** : Suppression automatique des anciennes entrées
- **Export** : JSON généré automatiquement (`rxx_history_export.json`)
- **Indexation** : Optimisation des requêtes temporelles

### **Fonctions principales :**

```python
# Stocker une nouvelle exécution
db.store_execution(donnees_enhanced, hypotheses, battery_matrix, idd, metadata)

# Récupérer l'historique d'un nœud
history = db.get_node_history("R11", days=30)

# Générer un dashboard
dashboard = db.generate_dashboard_data(days=7)

# Exporter en JSON
db.export_to_json("export_du_jour.json")

```

---

## 📂 **ARBORESCENCE COMPLÈTE**

```
C:\\hmn_dev\\carto\\dags\\
│
├── r_dynamo.py                    # SCRIPT PRINCIPAL V17.0
│
├── ontologie.csv                  # Définition des 63 nœuds
│
├── scripts/                       # Scripts de collecte (1 par nœud)
│   ├── r00_bitcoin.py
│   ├── r01_pib_chine.py
│   ├── r02_otan_budget.py
│   ├── r03_inflation_us.py
│   └── ... (60+ fichiers)
│
├── hypotheses/                    # Modules de validation
│   ├── h1_p4.py
│   ├── h2_otan.py
│   ├── h3_cyber_supply.py
│   └── ... (8 fichiers)
│
├── db_integration.py             # Module de base de données
│
├── rxx_history.db                # Base SQLite (créée automatiquement)
│
├── reports/                      # Rapports générés
│   ├── monitoring_enhanced.csv   # Données enrichies
│   ├── validation_report.json    # Rapport complet JSON
│   ├── hypotheses_check.json     # Résultats des hypothèses
│   └── validation_report.html    # Dashboard HTML
│
├── logs/                         # Journalisation
│   ├── execution_20260117.log
│   └── debug_final_v17.txt
│
└── README.md                     # Cette documentation

```

---

## 🔄 **CYCLE D'EXÉCUTION COMPLET**

```
1. INITIALISATION
   ├── Chargement ontologie.csv (63 nœuds)
   ├── Vérification des scripts
   └── Préparation structures données

2. EXÉCUTION PARALLÈLE
   ├── Pour chaque nœud prioritaire (🔴 → 🟡 → 🟢)
   ├── Lancement du script correspondant
   ├── Capture de la valeur retournée
   └── Enrichissement avec contexte

3. VALIDATION ÉPISTÉMIQUE
   ├── Test des 8 hypothèses
   ├── Calcul Battery Metals (6 métaux critiques)
   └── Calcul IDD (Indice de Décision Dynamique)

4. STOCKAGE & RAPPORTS
   ├── Sauvegarde dans rxx_history.db
   ├── Génération CSV enrichi
   ├── Génération JSON de rapport
   └── Création dashboard HTML

5. AFFICHAGE SYNTHÈSE
   ├── Dashboard prioritaire (alertes 🚨)
   ├── Statistiques V17.0
   └── Recommandations opérationnelles

```

---

## 🚨 **CODES COULEUR & SYMBOLES**

| Symbole | Signification | Action requise |
| --- | --- | --- |
| 🔴 | Critique | Intervention immédiate |
| 🟡 | Moyen | Surveillance accrue |
| 🟢 | Faible | Monitoring normal |
| 🚨 | Alerte seuil | Vérification manuelle |
| ✅ | Validé | Confirmation stratégique |
| ⚠️ | Mitigé | Analyse complémentaire |
| ❌ | Invalidé | Révision hypothèse |
| ↗️ | Hausse | Opportunité |
| ↘️ | Baisse | Risque |

---

## 📞 **DÉPANNAGE RAPIDE**

### **Problème : Script ne s'exécute pas**

```bash
# Tester manuellement le script
python scripts/r00_bitcoin.py

# Vérifier les permissions
chmod +x scripts/r00_bitcoin.py

# Vérifier les dépendances
pip install requests pandas

```

### **Problème : Valeur incorrecte**

1. Vérifier l'API source (est-elle accessible ?)
2. Vérifier le parsing du retour
3. Vérifier le format de sortie (uniquement le nombre)

### **Problème : Base de données corrompue**

```bash
# Sauvegarder
cp rxx_history.db rxx_history_backup.db

# Réinitialiser (perte de données)
rm rxx_history.db
python r_dynamo.py  # Recréation automatique

```

### **Problème : Performances lentes**

```python
# Dans ontologie.csv
Augmenter les 'intervalle' des nœuds non-critiques
Désactiver les nœuds obsolètes (script_path = "MANUEL")

```

---

## 🎖️ **BONNES PRATIQUES**

1. **Versionnement** : Toujours garder une copie de l'ontologie
2. **Monitoring** : Vérifier les logs après chaque exécution
3. **Maintenance** : Nettoyer régulièrement le dossier `reports/`
4. **Sauvegarde** : Exporter périodiquement la base SQLite
5. **Documentation** : Mettre à jour cette doc pour chaque nouveau nœud

---

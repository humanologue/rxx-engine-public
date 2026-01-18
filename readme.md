# 🚀 Rxx Engine V17.3 - GUIDE INSTALLATION & UTILISATION

## 📋 **PRÉREQUIS**
```
✅ Python 3.12+ (testé 3.12)
✅ Git (installé)
✅ pip (inclus avec Python)
✅ Accès internet (APIs/scripts)
✅ Windows/Linux/MacOS
```

## 🎯 **INSTALLATION (5min)**

### **1. CLONER REPO**
```bash
git clone https://github.com/humanologue/rxx-engine.git
cd rxx-engine
```

### **2. ENVIRONNEMENT VIRTUEL**
```bash
# Windows
python -m venv rxx_env
rxx_env\Scripts\activate

# Linux/Mac
python3 -m venv rxx_env  
source rxx_env/bin/activate
```

### **3. DÉPENDANCES**
```bash
pip install --upgrade pip
pip install -r requirements_r32.txt
pip install pandas numpy requests beautifulsoup4 lxml plotly
pip install yfinance pyyaml sqlite3
```

## ⚡ **UTILISATION**

### **Lancement Principal**
```bash
python Rxx_Engine_V17.0.py
```

**Sortie attendue** (72s) :
```
🚀 Rxx Engine V17.3 - VALIDATION ÉPISTÉMIQUE
📊 51/51 scripts exécutés
🔋 Battery Metals: 4/6 SUPERCYCLE
🚨 Cyber: R00=269 ZeroDays
🟢 IDD: 100/100 ROUTINE OK
✅ validation_report.html généré
```

## 📊 **FICHIERS GÉNÉRÉS (CRITIQUES)**

| Fichier | Contenu | Action |
|---------|---------|--------|
| `validation_report.html` | **DASHBOARD INTERACTIF** | Ouvrir navigateur |
| `monitoring_enhanced.csv` | **65 nœuds export** | Excel/analyse |
| `rxx_history.db` | **100 runs historiques** | SQLite |
| `hypotheses_check.json` | **8 hypothèses DYNAMO** | JSON viewer |

## 🔧 **CADENCE MONITORING RECOMMANDÉE**

```bash
# QUOTIDIEN 6h
0 6 * * * cd /path/to/rxx-engine && git pull && python Rxx_Engine_V17.0.py

# 12h/18h focus Battery/Cyber
0 12,18 * * * cd /path/to/rxx-engine && python Rxx_Engine_V17.0.py
```

## 🎛️ **COMMANDE DEBUG & ANALYSE**

```bash
# Analyse DB historique
python analyse_db.py

# Dashboard avancé Plotly
python dashboard_advanced.py

# Test scripts individuels
python r66_lithium.py    # Lithium CNY/T
python r00_zeroday.py    # ZeroDays CVE
```

## 🚨 **ALERTES CRITIQUES V17.3**

```
🔋 BATTERY SUPERCYCLE 4/6:
✅ R66 Lithium: 159.5k CNY/T → LONG
✅ R70 Rare Earths: 61$/kg → LONG

🚨 CYBER THREATS:
🔴 R00=269 ZeroDays → AUDIT IOC
🔴 R92=100 C2 domains → BLOCKLIST
```

## 💾 **MAINTENANCE**

```bash
# Mise à jour Git
git pull origin main

# Cache clean (optionnel)
rm -rf cache/*.pkl __pycache__/

# Backup DB
cp rxx_history.db rxx_history_$(date +%Y%m%d).db
```

## 🛠️ **DÉPANNAGE RAPIDE**

| Problème | Solution |
|----------|----------|
| `ModuleNotFoundError` | `pip install -r requirements_r32.txt` |
| `API timeout` | Vérifier internet + `pip install --upgrade requests` |
| `R98 lent (16s)` | Normal IMD Drought API |
| `R84 lent (12s)` | Normal USDA Cereals API |
| **Dashboard vide** | Ouvrir `validation_report.html` |

## 📈 **INTERPRÉTATION RÉSULTATS**

```
🟢 IDD 100/100 → ROUTINE OK
🟢 Battery 4/6 → SUPERCYCLE (ACCUMULATION)
🚨 R00>15 → CYBER SURVEILLANCE
📊 H1/H2/H3/H5/H6/H11 → Système nominal
```

## 🌐 **Ressources**
```
📂 GitHub: https://github.com/humanologue/rxx-engine
🗃️ DB: rxx_history.db (SQLite)
📊 Ontologie: ontologie.json (65 nœuds)
📋 Scripts: 51 sources temps réel
```

***

**💾 Copiez ce document → `README.md` → `git add README.md && git commit -m "Documentation installation V17.3" && git push`**

**Rxx Engine V17.3 = PLUG & PLAY → `python Rxx_Engine_V17.0.py` → Dashboard prêt** 🎯

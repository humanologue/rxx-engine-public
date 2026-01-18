# **README.md COMPLET - RXX ENGINE V17.0**

```markdown
<div align="center">

# 🚀 RXX Engine V17.0 - Monitoring Géopolitique Temps Réel

[![IDD Status](https://img.shields.io/badge/IDD-100%25-brightgreen.svg)]()
[![Hypothèses](https://img.shields.io/badge/Hypothèses-6%2F8-blue.svg)]()
[![GDELT](https://img.shields.io/badge/R32-1140%20%C3%A9v%C3%A9nements-red.svg)]()
[![Battery](https://img.shields.io/badge/Battery-4%2F6%20SUPERCYCLE-orange.svg)]()

**Système de monitoring stratégique 65 nœuds**  
**Économie • Géopolitique • Énergie • Métaux • Cyber • Agri/Env**

[Documentation](doc/documentation.md) • [Démo Dashboard](validation_report.html) • [GitHub Actions](https://github.com/humanologue/rxx-engine/actions)

</div>

## 🎯 Aperçu

**RXX Engine** monitore **65 indicateurs critiques** en temps réel :

| **Domaine** | **Exemples** | **Source** |
|-------------|--------------|------------|
| **Géopolitique** | R32 GDELT (1140 événements Code18) • OTAN • Carriers US | GDELT, SIPRI, USNI |
| **Économie** | PBOC ($48T) • BTC/ETH • Fear&Greed (49) • DXY (99.38) | PBOC, CoinMarketCap |
| **Énergie** | Brent ($64) • OPEC (92%) • LNG Russie (51%) • TTF (€37) | IEA, OPEC, EIA |
| **Métaux** | **Li ($159k/t) • Ag ($89/oz) • Ni/Co** | **SUPERCYCLE 4/6** |
| **Cyber** | Zero-days (269) • IOC (450) • C2 DNS (100) | CISA, VirusTotal |
| **Agri/Env** | Séismes M6+ (2) • Sécheresse IMD (14%) • Forêts (-10.9%) | USGS, IMD, FAO |

**Score IDD : 100/100** 🟢 **ROUTINE OK**

## 🔥 Fonctionnalités Clés

- **Validation Épistémique** : 8 hypothèses DYNAMO testées automatiquement
- **GDELT R32** : 1140 événements Code18 mondial (quota robuste)
- **Battery Metals** : Supercycle détecté **4/6** (Li/Ag/Ni/Co)
- **Alertes Temps Réel** : Cyber (R00=269↑), Énergie (R11=51%↓)
- **Base Historique** : 104 exécutions (rxx_history.db)
- **Dashboard Interactif** : [validation_report.html](validation_report.html)

## 📊 Hypothèses DYNAMO v2.4 (6/8 ✅)

| **Hypothèse** | **Statut** | **Indicateurs** |
|---------------|------------|-----------------|
| H1_P4 | ✅ | R11=51% • R24=€37 |
| H2_OTAN | ✅ | R02=4638 > 4000 |
| H3_CYBER | ✅ | R00=269 • R81=450 |
| **H5_GDELT** | ✅ | **R32=1140 événements** |
| H6_CH_Afrique | ✅ | R01=48T$ |
| H11_SCW | ✅ | R71=0.997B$ |

## 🎛️ Installation & Utilisation

### Prérequis
```bash
Python 3.11+ -  Git -  BigQuery Console (optionnel)
pip install -r requirements.txt
```

### Démarrage (2 min)
```bash
# Clone + install
git clone https://github.com/humanologue/rxx-engine.git
cd rxx-engine
pip install -r requirements.txt

# Données GDELT manuelles (quota robuste)
# BigQuery Console → rootcodes_7j.csv → db_local/

# Lancement
python Rxx_Engine_V17.0.py
```

### Routine Quotidienne (14h)
```bash
# 1. BigQuery → rootcodes_7j.csv (5min)
# 2. Exécution
python Rxx_Engine_V17.0.py
# 3. GitHub
git add . && git commit -m "RXX $(date +%Y%m%d)" && git push
```

## 🛠️ Structure du Projet

```
rxx-engine/
├── Rxx_Engine_V17.0.py      # Moteur principal IDD 100
├── r32_gdelt.py             # R32 GDELT (1140|-6.2)
├── ontologie.json           # 65 nœuds pipeline
├── db_local/                # Données (ignoré .gitignore)
│   └── rootcodes_7j.csv     # GDELT 35 lignes réelles
├── doc/                     # Documentation complète
├── validation_report.html   # Dashboard interactif
└── rxx_history.db          # 104 exécutions historiques
```

## 📈 Résultats V17.0 (18/01)

```
🎯 IDD: 100.0/100 🟢 ROUTINE OK
📊 Nœuds: 65 | Scripts: 51/65 OK
✅ H5_GDELT: R32=1140 événements Code18
🔋 Battery: 4/6 SUPERCYCLE (Li/Ag/Ni/Co)
🚨 Alertes: R00=269 zero-days ↑ | R92=100 C2 DNS
⏱️ Timing: 98s (R98=28s, R99=19s)
```

## 🔮 Signaux Stratégiques

```
🟢 Battery Metals SUPERCYCLE → ACCUMULATION AGRESSIVE
🟢 Chine PBOC $48T → Stable
🟢 OTAN R02=4638 → Effort militaire ↑
🟡 Cyber R00=269 zero-days → Vigilance
🟡 LNG Russie 51% → Dépendance persistante
```

## 🤝 Contributing

1. **Fork** le projet
2. **BigQuery** → `rootcodes_7j.csv` à jour
3. **Test** `python Rxx_Engine_V17.0.py`
4. **PR** vers `main`

## 📄 Licence

[MIT](LICENSE) - Utilisation libre recherche/monitoring

## 👥 Auteurs

**humanologue** - Monitoring géopolitique IA  
[github.com/humanologue](https://github.com/humanologue)  
**V17.0** - 18/01/2026 - IDD 100/100

---

<div align="center">

[![GitHub stars](https://img.shields.io/github/stars/humanologue/rxx-engine?style=social)](https://github.com/humanologue/rxx-engine)
[![GitHub forks](https://img.shields.io/github/forks/humanologue/rxx-engine?style=social)](https://github.com/humanologue/rxx-engine)

**🚀 RXX Engine V17.0 - Géopolitique en Temps Réel**

</div>
```


```

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Rxx Engine V15.0 - Gestion formats étendus
"""

import os
import re
import json
import pandas as pd
from datetime import datetime
from pathlib import Path
import subprocess
import sys

DIR_SCRIPTS = Path.cwd()
ONTOLOGIE_FILE = DIR_SCRIPTS / "ontologie.json"
CSV_OUTPUT = DIR_SCRIPTS / "monitoring.csv"
DEBUG_FILE = DIR_SCRIPTS / "debug_final_v15.txt"
DATE_NOW = datetime.now().strftime("%Y-%m-%d %H:%M CET")

# Forcer UTF-8 pour Windows
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# MAPPING SCRIPT -> NODE
SCRIPT_TO_NODE_MAPPING = {
    "r00_zeroday.py": "R00", 
    "r01_pboc.py": "R01", 
    "r02_sipri.py": "R02",
    "r03_ethereum.py": "R03",
    "r04_usni.py": "R04",
    "r05_suez_canal.py": "R05",
    "r06_napoleon.py": "R06", 
    "r07_vz_oil.py": "R07", 
    "r09_brent.py": "R09",
    "r10_vix_cboe.py": "R10",
    "r11_gas_storage.py": "R11", 
    "r12_fear_greed.py": "R12", 
    "r13_opec_global.py": "R13",
    "r15_bitcoin.py": "R15", 
    "r16_libya_oil.py": "R16", 
    "r17_redsea_pirates.py": "R17",
    "r24_ttf.py": "R24", 
    "r25_vnz_chine.py": "R25", 
    "r28_seismic_m6.py": "R28",
    "r32_gdelt.py": "R32", 
    "r32_17_repression.py": "R32_17", 
    "r32_18_geo.py": "R32_18",
    "r32_20_manif.py": "R32_20", 
    "r33_acled_riots.py": "R33", 
    "r33_gdelt19_acled.py": "R33_acled",
    "r36_usni_carriers.py": "R36", 
    "r58_dxy.py": "R58", 
    "r65_silver.py": "R65",
    "r65_silver_pv.py": "R65_pv", 
    "r66_lithium.py": "R66", 
    "r66_lithium_pv.py": "R66_pv",
    "r67_nickel.py": "R67", 
    "r68_cobalt.py": "R68", 
    "r69_graphite.py": "R69",
    "r70_rare_earths.py": "R70", 
    "r71_usd1_wlfi.py": "R71", 
    "r74_forets_fao.py": "R74",
    "r76_water.py": "R76", 
    "r81_ioc.py": "R81", 
    "r82_shadowserver.py": "R82",
    "r84_cereals_usda.py": "R84", 
    "r85_soil_degradation.py": "R85", 
    "r91_isc.py": "R91",
    "r92_dns_c2.py": "R92", 
    "r95_ttp.py": "R95", 
    "r96_hibp_breaches.py": "R96",
    "r97_yara_rules.py": "R97", 
    "r98_imd_drought.py": "R98", 
    "r99_moussons_imd.py": "R99",
    "r125_pathogenes_ecdc.py": "R125", 
    "r127_niveau_mer_psmsl.py": "R127",
    "r200_climat_era5.py": "R200", 
    "r201_energie_iea.py": "R201",
}

# COMMANDES ÉTENDUES avec formats complets
COMMANDES_ETENDUES = {
    "r00_zeroday.py": ('python -c "from r00_zeroday import scrape_r00; r=scrape_r00()[0]; print(f\'R00={r[\\"zeroday_cve\\"]} | Fresh={r[\\"fresh_h\\"]}h LIVE\')"', r'R00=(\d+)'),
    "r01_pboc.py": ('python -c "from r01_pboc import scrape_r01; r=scrape_r01()[0]; print(f\'R01 PBOC={r.get(\\"pboc_assets_cny_t\\")}T CNY (${r.get(\\"pboc_assets_usd_t\\")}T) | {r[\\"status\\"]}\')"', r'PBOC=(\d+\.?\d*)'),
    "r02_sipri.py": ('python -c "from r02_sipri import scrape_r02; r=scrape_r02()[0]; print(f\'R02 TIV={r[\\"sipri_tiv_total\\"]} | {r[\\"top_suppliers\\"]}→{r[\\"top_recipients\\"]} | USA-UKR={r[\\"usa_ukr_tiv\\"]}\')"', r'TIV=(\d+)'),
    "r03_ethereum.py": ('python -c "from r03_ethereum import scrape_r03; r=scrape_r03()[0]; print(f\'R03 ETH=${r[\\"ethereum_usd\\"]:,.0f}\')"', r'ETH=\$([\d,]+)'),
    "r04_usni.py": ('python -c "from r04_usni import scrape_r04; r=scrape_r04()[0]; print(f\'R04 PLA={r[\\"pla_navy_total\\"]} | CV={r[\\"carriers\\"]} DDG={r[\\"destroyers_055\\"]+r[\\"destroyers_052d\\"]} FFG={r[\\"frigates_054a\\"]+r[\\"frigates_054b\\"]}\')"', r'PLA=(\d+)'),
    "r05_suez_canal.py": ('python -c "from r05_suez_canal import scrape_r05; print(f\'R05 Suez={scrape_r05()} navires/jour | Fresh=24h\')"', r'Suez=(\d+)'),
    "r06_napoleon.py": ('python -c "from r06_napoleon import scrape_r06; print(f\'R06 Napoléon={scrape_r06()}€ AuCOFFRE\')"', r'=([\d.]+)€'),
    "r07_vz_oil.py": ('python -c "from r07_vz_oil import scrape_r07; print(f\'R07 VZ Oil={scrape_r07()} Mbpd OPEC\')"', r'Oil=(\d+\.?\d*)'),
    "r09_brent.py": ('python -c "from r09_brent import scrape_r09; r=scrape_r09()[0]; print(f\'R09 Brent=${r.get(\\"brent_price_usd\\", \\"FAIL\\")} via {r.get(\\"method\\", \\"-\\")}\')"', r'Brent=\$(\d+\.?\d*)'),
    "r10_vix_cboe.py": ('python -c "from r10_vix import scrape_r10; r=scrape_r10(); print(f\'R10 VIX={r.get(\\"value\\", 0)} | Fresh=24h\')"', r'VIX=(\d+\.?\d*)'),
    "r11_gas_storage.py": ('python -c "from r11_gas_storage import scrape_r11; r=scrape_r11()[0]; print(f\'R11={r[\\"gas_storage_pct\\"]}% TRL9 | Fresh={r[\\"freshness_days\\"]}d | Validé={r[\\"validated_date\\"]} | {r[\\"threshold_20pct\\"]}\')"', r'R11=(\d+\.?\d*)%'),
    "r12_fear_greed.py": ('python -c "from r12_fear_greed import scrape_r12; r=scrape_r12()[0]; print(f\'R12 FGI={r[\\"fear_greed_index\\"]} | {r[\\"status\\"]}\')"', r'FGI=(\d+)'),
    "r13_opec_global.py": ('python -c "from r13_opec_global import scrape_r13; print(f\'R13 OPEC={scrape_r13()}% compliance\')"', r'OPEC=(\d+)%'),
    "r15_bitcoin.py": ('python -c "from r15_bitcoin import scrape_r15; r=scrape_r15()[0]; print(f\'R15 BTC=${r[\\"bitcoin_price_usd\\"]:,} | Δ{r[\\"change_24h_pct\\"]:+.1f}% | MC ${r[\\"market_cap_usd_t\\"]}T\')"', r'BTC=\$([\d,]+)'),
    "r16_libya_oil.py": ('python -c "from r16_libya_oil import scrape_r16; print(f\'R16 Libye={scrape_r16()} Mbpd OPEC\')"', r'Libye=(\d+\.?\d*)'),
    "r17_redsea_pirates.py": ('python -c "from r17_redsea_pirates import scrape_r17; r=scrape_r17(); print(f\'R17 RedSea={r[\\"tankers_24h\\"]} tankers/24h | Fresh=24h\')"', r'RedSea=(\d+)'),
    "r24_ttf.py": ('python -c "from r24_ttf import scrape_r24; r=scrape_r24()[0]; print(f\'R24 TTF=€{r.get(\\"ttf_gas_eur_mwh\\", \\"FAIL\\")}/MWh | {r.get(\\"status\\", \\"-\\")}\')"', r'TTF=€(\d+\.?\d*)'),
    "r25_vnz_chine.py": ('python -c "from r25_vnz_chine import scrape_r25; print(f\'R25 VZ→Chine={scrape_r25()} kbpd | Fresh=24h\')"', r'VZ→Chine=(\d+)'),
    "r28_seismic_m6.py": ('python -c "from r28_seismic_m6 import scrape_r28; print(f\'R28 M6+={scrape_r28()} événements/30j | Fresh=24h\')"', r'M6\+=(\d+)'),
    "r32_gdelt.py": ('python -c "from r32_gdelt import scrape_r32; r=scrape_r32()[0]; print(f\'R32 GDELT18={r[\\"gdelt_events_18\\"]} | Tone={r[\\"avg_tone_pts\\"]}pts | {r[\\"alert_status\\"]} | {r[\\"status\\"]}\')"', r'GDELT18=(\d+)'),
    "r32_17_repression.py": ('python -c "from r32_17_repression import scrape_r32_17; print(scrape_r32_17())"', r'(\d+)\s*\|'),
    "r32_18_geo.py": ('python -c "from r32_18_geo import scrape_r32_18_geo; print(scrape_r32_18_geo())"', r'(\d+)\s*\|'),
    "r32_20_manif.py": ('python -c "from r32_20_manif import scrape_r32_20; print(scrape_r32_20())"', r'(\d+)\s*\|'),
    "r33_acled_riots.py": ('python -c "from r33_acled_riots import scrape_r33; print(f\'R33 ACLED={scrape_r33()}\')"', r'ACLED=(\d+)'),
    "r33_gdelt19_acled.py": ('python -c "from r33_gdelt19_acled import scrape_r33; print(f\'R33 Riots={scrape_r33()} événements/24h | Fresh=24h\')"', r'Riots=(\d+)'),
    "r36_usni_carriers.py": ('python -c "from r36_usni_carriers import scrape_r36; print(f\'R36 USNI={scrape_r36()}\')"', r'USNI=(\d+)'),
    "r58_dxy.py": ('python -c "from r58_dxy import scrape_r58; r=scrape_r58()[0]; print(f\'R58 DXY={r[\\"dxy_index\\"]} {r[\\"method\\"]}\')"', r'DXY=(\d+\.?\d*)'),
    "r65_silver.py": ('python -c "from r65_silver import scrape_r65; print(f\'R65 Ag=${scrape_r65()}\')"', r'Ag=\$(\d+\.?\d*)'),
    "r65_silver_pv.py": ('python -c "from r65_silver_pv import scrape_r65; r=scrape_r65()[0]; print(f\'R65 Ag PV={r[\\"silver_pv_kt\\"]}kt | Total={r[\\"silver_total_kt\\"]}kt | PV={r[\\"pv_share_pct\\"]}% | Fresh={r[\\"freshness_days\\"]}d\')"', r'Ag PV=(\d+)kt'),
    "r66_lithium.py": ('python -c "from r66_lithium import scrape_r66; print(f\'R66 Li={scrape_r66()}k\')"', r'Li=(\d+)k'),
    "r66_lithium_pv.py": ('python -c "from r66_lithium_pv import scrape_r66; r=scrape_r66()[0]; print(f\'R66 Li={r[\\"lithium_mine_kt\\"]}kt | Déficit={r[\\"deficit_kt\\"]}kt | AU={r[\\"australia_kt\\"]}kt | Fresh={r[\\"fresh_days\\"]}d NON-RT\')"', r'Li=(\d+)kt'),
    "r67_nickel.py": ('python -c "from r67_nickel import scrape_r67; print(f\'R67 Ni=${scrape_r67()}\')"', r'Ni=\$(\d+)'),
    "r68_cobalt.py": ('python -c "from r68_cobalt import scrape_r68; print(f\'R68 Co=${scrape_r68()}\')"', r'Co=\$(\d+)'),
    "r69_graphite.py": ('python -c "from r69_graphite import scrape_r69; print(f\'R69 Graphite=${scrape_r69()}\')"', r'Graphite=\$(\d+)'),
    "r70_rare_earths.py": ('python -c "from r70_rare_earths import scrape_r70; print(f\'R70 RE=${scrape_r70()}k\')"', r'RE=\$(\d+)k'),
    "r71_usd1_wlfi.py": ('python -c "from r71_usd1_wlfi import scrape_r71; r=scrape_r71()[0]; print(f\'R71 USD1=${r[\\"usd1_wlfi_price\\"]:.4f}\')"', r'USD1=\$(\d+\.?\d*)'),
    "r74_forets_fao.py": ('python -c "from r74_forets_fao import scrape_r74; r=scrape_r74(); print(f\'R74 Forêts={r[\\"loss_mha_yr\\"]} Mha/an | {r[\\"period\\"]} | {r[\\"validation\\"]} | Fresh={r[\\"fresh_days\\"]}j\')"', r'Forêts=(\d+\.?\d*)'),
    "r76_water.py": ('python -c "from r76_water import scrape_r76; r=scrape_r76()[0]; print(f\'R76 Eau={r[\\"water_km3\\"]}km³ | Access={r[\\"access_pct\\"]}% | Fresh={r[\\"fresh_days\\"]}d NON-RT | Stress={r[\\"stress_b\\"]}B\')"', r'Eau=(\d+)km'),
    "r81_ioc.py": ('python -c "from r81_ioc import scrape_r81; r=scrape_r81()[0]; print(f\'R81={r[\\"ioc_vt\\"]} | Fresh={r[\\"fresh_h\\"]}h | Method={r[\\"method\\"]}\')"', r'R81=(\d+)'),
    "r82_shadowserver.py": ('python -c "from r82_shadowserver import scrape_r82; print(f\'R82 CVEs={scrape_r82()}/24h\')"', r'CVEs=(\d+)'),
    "r84_cereals_usda.py": ('python -c "from r84_cereals_usda import scrape_r84; r=scrape_r84(); print(f\'R84={r[\\"final_mt\\"]} Mt | Sources={r[\\"computed\\"][\\"valid_sources\\"]} | Method={r[\\"computed\\"][\\"method\\"]} | Fresh={r[\\"fresh_days\\"]}j\')"', r'R84=(\d+) Mt'),
    "r85_soil_degradation.py": ('python -c "from r85_soil_degradation import scrape_r85; r=scrape_r85(); print(f\'R85={r[\\"final_sdi\\"]} | Sources={r[\\"computed\\"][\\"valid_sources\\"]} | Method={r[\\"computed\\"][\\"method\\"]} | Pop={r[\\"population_affected\\"]}B\')"', r'R85=(\d+\.?\d*)'),
    "r91_isc.py": ('python -c "from r91_isc import scrape_r91; r=scrape_r91()[0]; print(f\'R91={r[\\"netflow_ir\\"]:,} | Fresh={r[\\"fresh_h\\"]}h | Method={r[\\"method\\"]}\')"', r'R91=([\d,]+)'),
    "r92_dns_c2.py": ('python -c "from r92_dns_c2 import scrape_r92; r=scrape_r92(); print(f\'R92={r[\\"final\\"]} | Sources={r[\\"computed\\"][\\"valid_sources\\"]} | Method={r[\\"computed\\"][\\"method\\"]} | Fresh={r[\\"fresh_h\\"]}h\')"', r'R92=(\d+)'),
    "r95_ttp.py": ('python -c "from r95_ttp import scrape_r95; r=scrape_r95()[0]; print(f\'R95={r[\\"new_ttps\\"]} | Fresh={r[\\"fresh_h\\"]}h LIVE\')"', r'R95=(\d+)'),
    "r96_hibp_breaches.py": ('python -c "from r96_hibp_breaches import scrape_r96; print(f\'R96 HIBP={scrape_r96()} breaches/24h | Fresh=24h\')"', r'HIBP=(\d+)'),
    "r97_yara_rules.py": ('python -c "from r97_yara_rules import scrape_r97; print(f\'R97 YARA={scrape_r97()} | Fresh=24h\')"', r'YARA=(\d+)'),
    "r98_imd_drought.py": ('python -c "from r98_imd_drought import scrape_r98; r=scrape_r98(); print(f\'R98={r[\\"final_deficit_pct\\"]}% | Sources={r[\\"computed\\"][\\"valid_sources\\"]} | Method={r[\\"computed\\"][\\"method\\"]} | LPA={r[\\"rainfall_pct_lpa\\"]}%)\')"', r'R98=(\d+\.?\d*)%'),
    "r99_moussons_imd.py": ('python -c "from r99_moussons_imd import scrape_r99; r=scrape_r99(); print(f\'R99={r[\\"final_pct\\"]}% LPA | Sources={r[\\"computed\\"][\\"valid_sources\\"]} | Method={r[\\"computed\\"][\\"method\\"]} | Fresh={r[\\"fresh_h\\"]}h\')"', r'R99=(\d+\.?\d*)%'),
    "r125_pathogenes_ecdc.py": ('python -c "from r125_pathogenes_ecdc import scrape_r125; print(f\'R125 Pathogènes={scrape_r125()} signalements/24h | Fresh=24h\')"', r'Pathogènes=(\d+)'),
    "r127_niveau_mer_psmsl.py": ('python -c "from r127_niveau_mer_psmsl import scrape_r127; r=scrape_r127(); print(f\'R127={r[\\"slr_mm_yr\\"]} mm/an | Stations={r[\\"source_stations\\"]} | {r[\\"validation\\"]} | Fresh={r[\\"fresh_h\\"]}h\')"', r'R127=(\d+\.?\d*) mm'),
    "r200_climat_era5.py": ('python -c "from r200_climat_era5 import scrape_r200; r=scrape_r200(); print(f\'R200={r[\\"final\\"]}°C | Sources={r[\\"computed\\"][\\"valid_sources\\"]} | Method={r[\\"computed\\"][\\"method\\"]} | Fresh={r[\\"fresh_h\\"]}h\')"', r'R200=([\d.,]+)°C'),
    "r201_energie_iea.py": ('python -c "from r201_energie_iea import scrape_r201; print(f\'R201 Énergie={scrape_r201()} TWh/an | Fresh=24h\')"', r'Énergie=(\d+)'),
}

def debug_log(msg):
    """Log avec encoding UTF-8"""
    with open(DEBUG_FILE, 'a', encoding='utf-8', errors='replace') as f:
        timestamp = datetime.now().strftime('%H:%M:%S')
        f.write(f"[{timestamp}] {msg}\n")

def executer_commande_etendue(script_name, node_id):
    """Exécute commande étendue qui retourne des infos formatées"""
    if script_name not in COMMANDES_ETENDUES:
        debug_log(f"⚠️  Pas de commande étendue pour {script_name}")
        return "NO_COMMAND", ""
    
    cmd, _ = COMMANDES_ETENDUES[script_name]
    debug_log(f"🚀 {node_id}: {cmd[:80]}...")
    
    try:
        # Forcer UTF-8 pour l'exécution
        env = os.environ.copy()
        env['PYTHONUTF8'] = '1'
        
        result = subprocess.run(
            cmd,
            shell=True,
            cwd=DIR_SCRIPTS,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=60,
            encoding='utf-8',
            errors='replace',
            env=env
        )
        
        output = result.stdout.strip()
        debug_log(f"📤 {node_id} sortie: {output}")
        
        if result.stderr:
            debug_log(f"❌ {node_id} stderr: {result.stderr[:200]}")
        
        if result.returncode == 0:
            return "OK", output
        else:
            return f"ERR{result.returncode}", output
    
    except subprocess.TimeoutExpired:
        debug_log(f"⏰ {node_id} timeout")
        return "TIMEOUT", ""
    except Exception as e:
        debug_log(f"💥 {node_id} exception: {str(e)}")
        return "EXCEPTION", str(e)

def extraire_valeur_etendue(output, node_id, script_name):
    """Extraction intelligente depuis sorties formatées"""
    if not output or output == "None":
        return "NO_OUTPUT"
    
    debug_log(f"🔍 {node_id} extraction depuis: '{output}'")
    
    # Nettoyer l'output
    cleaned = output.strip()
    
    # Essayer d'abord avec le pattern spécifique
    if script_name in COMMANDES_ETENDUES:
        _, pattern = COMMANDES_ETENDUES[script_name]
        match = re.search(pattern, cleaned)
        if match:
            valeur = match.group(1).replace(',', '')
            debug_log(f"  ✓ Pattern étendu: {valeur}")
            return valeur
    
    # Patterns génériques pour les formats Rxx=value
    patterns_generiques = [
        r'R\d+\s*=\s*([\d.,]+)',  # R00=123
        r'=\s*([\d.,]+)[\s|]',    # =123 |
        r'([\d.,]+)\s*[°%€$]',    # 123°C, 123%, 123€, 123$
        r'(\d+\.?\d*)\s*(?:T|M|k|m|%|°|€|\$)',  # 123T, 123M, 123k, 123%
    ]
    
    for pattern in patterns_generiques:
        match = re.search(pattern, cleaned)
        if match:
            valeur = match.group(1).replace(',', '.')
            debug_log(f"  ✓ Pattern générique: {valeur}")
            return valeur
    
    # Dernier recours: chercher n'importe quel nombre
    match = re.search(r'(\d+\.?\d*)', cleaned)
    if match:
        valeur = match.group(1)
        debug_log(f"  ✓ Nombre trouvé: {valeur}")
        return valeur
    
    debug_log(f"  ✗ Aucune valeur numérique trouvée")
    return cleaned[:50]  # Retourne le début pour debug

def main():
    """Méthode principale V15.0"""
    if DEBUG_FILE.exists():
        DEBUG_FILE.unlink()
    
    debug_log(f"🚀 ENGINE V15.0 - Démarrage {DATE_NOW}")
    print(f"\n{'='*80}")
    print(f"🚀 Rxx Engine V15.0 - GESTION FORMATS ÉTENDUS")
    print(f"📅 {DATE_NOW}")
    print(f"{'='*80}")
    
    # Charger ontologie
    try:
        with open(ONTOLOGIE_FILE, 'r', encoding='utf-8') as f:
            ontologie = json.load(f)
        nodes = ontologie.get("noeuds", {})
        print(f"📁 Ontologie: {len(nodes)} nœuds")
    except Exception as e:
        print(f"❌ Erreur ontologie: {e}")
        return
    
    # Exécuter les scripts
    donnees_live = {}

    print(f"\n⚡ EXÉCUTION FORMATS ÉTENDUS:")

    for script_name, node_id in sorted(SCRIPT_TO_NODE_MAPPING.items()):
        if not Path(script_name).exists():
            print(f"  ❌ {node_id:8} - Script manquant: {script_name}")
            donnees_live[node_id] = {"valeur": "SCRIPT_MISSING", "statut": "NO_FILE", "output": ""}
            continue
        
        # Infos du nœud
        node_info = nodes.get(node_id, {})
        priorite = node_info.get("priorite", "🟡")
        domaine = node_info.get("domaine", "")
        
        print(f"  ▶️  {node_id:8} {priorite} {domaine:12}", end=" ", flush=True)
        
        # Exécution avec format étendu
        statut, output = executer_commande_etendue(script_name, node_id)
        valeur = extraire_valeur_etendue(output, node_id, script_name)
        
        donnees_live[node_id] = {
            "valeur": valeur,
            "statut": statut,
            "script": script_name,
            "output": output[:100]
        }
        
        print(f"[{statut:10}] → {valeur}")
    
    # Ajouter nœuds manuels
    print(f"\n📝 NŒUDS MANUELS:")
    manuels_count = 0
    for node_id, node in nodes.items():
        if node_id not in donnees_live:
            valeur_manuelle = node.get("valeur_live", "MANUEL")
            if valeur_manuelle != "MANUEL":
                print(f"  📍 {node_id:8} → {valeur_manuelle} (pré-configuré)")
                donnees_live[node_id] = {
                    "valeur": str(valeur_manuelle),
                    "statut": "MANUEL",
                    "script": node.get("file", ""),
                    "output": "PRECONFIG"
                }
                manuels_count += 1
            elif node.get("statut_live") == "LIVE":
                print(f"  ⚠️  {node_id:8} → MANUEL (mais marqué LIVE)")
                donnees_live[node_id] = {
                    "valeur": "MANUEL",
                    "statut": "MANUEL",
                    "script": node.get("file", ""),
                    "output": "LIVE_MANUAL"
                }
                manuels_count += 1
    
    # Générer CSV
    print(f"\n📊 GÉNÉRATION CSV...")
    
    rows = []
    for node_id, node in nodes.items():
        live = donnees_live.get(node_id, {})
        
        row = {
            "node_id": node_id,
            "donnee": node.get("donnee", ""),
            "domaine": node.get("domaine", ""),
            "priorite": node.get("priorite", ""),
            "valeur_live": live.get("valeur", node.get("valeur_live", "MANUEL")),
            "statut_exec": live.get("statut", "MANUEL"),
            "script_utilise": live.get("script", node.get("file", "")),
            "output_tronque": live.get("output", ""),
            "seuil": node.get("seuil", ""),
            "timestamp": DATE_NOW
        }
        rows.append(row)
    
    df = pd.DataFrame(rows)
    
    # Trier
    priority_order = {"🔴": 0, "🟡": 1, "🟢": 2, "": 3}
    df['priority_num'] = df['priorite'].map(priority_order)
    df = df.sort_values(['priority_num', 'domaine', 'node_id'])
    df = df.drop('priority_num', axis=1)
    
    df.to_csv(CSV_OUTPUT, index=False, sep=';', encoding='utf-8')
    
    # Statistiques
    total = len(nodes)
    executes = len([v for v in donnees_live.values() if v["statut"] not in ["MANUEL", "NO_FILE"]])
    succes = len([v for v in donnees_live.values() if v["statut"] == "OK"])
    valeurs_numeriques = len([v for v in donnees_live.values() 
                            if v["valeur"] and re.match(r'^\d+\.?\d*$', str(v["valeur"]))])
    
    print(f"\n📈 STATISTIQUES:")
    print(f"   Nœuds totaux: {total}")
    print(f"   Scripts exécutés: {executes}")
    print(f"   Succès d'exécution: {succes}")
    print(f"   Valeurs numériques: {valeurs_numeriques}")
    print(f"   Nœuds manuels: {manuels_count}")
    print(f"   CSV généré: {CSV_OUTPUT}")
    print(f"   Debug complet: {DEBUG_FILE}")
    
    # Alertes prioritaires
    print(f"\n🎯 ALERTES PRIORITAIRES (🔴):")
    alertes = [(node_id, data) for node_id, data in donnees_live.items() 
               if nodes.get(node_id, {}).get("priorite") == "🔴"]
    
    for node_id, data in alertes:
        valeur = data["valeur"]
        seuil = nodes.get(node_id, {}).get("seuil", "")
        try:
            # Tenter de comparer numérique
            valeur_clean = str(valeur).replace(',', '.')
            if re.match(r'^\d+\.?\d*$', valeur_clean) and '>' in str(seuil):
                valeur_num = float(valeur_clean)
                seuil_num = float(re.search(r'(\d+\.?\d*)', str(seuil)).group(1))
                emoji = "🚨" if valeur_num > seuil_num else "✅"
            else:
                emoji = "📊"
        except Exception:
            emoji = "⚠️"
        
        print(f"  {emoji} {node_id:8} → {valeur:15} (seuil: {seuil})")
    
    # DASHBOARD PRIORITAIRE
    print("\n📊 DASHBOARD PRIORITAIRE:")
    print("="*80)
    
    # Filtrer les priorités 🔴
    prioritaires = df[df["priorite"] == "🔴"][["node_id", "valeur_live", "domaine", "priorite", "seuil"]].head(10)
    
    for idx, row in prioritaires.iterrows():
        try:
            valeur = str(row['valeur_live'])
            if valeur not in ["MANUEL", "NO_FILE", "NO_OUTPUT"] and re.match(r'^\d+\.?\d*$', valeur):
                valeur_num = float(valeur)
                seuil_str = str(row['seuil'])
                if '>' in seuil_str:
                    seuil_num = float(re.search(r'(\d+\.?\d*)', seuil_str).group(1))
                    emoji = "🚨" if valeur_num > seuil_num else "✅"
                else:
                    emoji = "📊"
            else:
                emoji = "📊"
        except:
            emoji = "⚠️"
        
        print(f"{emoji} {row['node_id']:>6} {str(row['valeur_live']):>10} {row['domaine']:>12} {row['priorite']}")
    
    print("="*80)
    
    # Générer HTML (optionnel)
    try:
        df.to_html("monitoring.html", index=False)
        print("🌐 monitoring.html généré (ouvrez dans navigateur)")
    except:
        pass
    
    print(f"\n💡 RÉCAPITULATIF V15.0:")
    print("  • Compatible formats étendus des scripts")
    print("  • Extraction intelligente des valeurs")
    print("  • Fix encoding UTF-8 pour Windows")
    print("  • Consultez debug_final_v15.txt pour détails")
    print("="*80)

if __name__ == "__main__":
    main()
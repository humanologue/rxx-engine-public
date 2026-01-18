#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Rxx Engine V17.0 - Validation Épistémique Intégrée
✅ Intelligence CARTO/DYNAMO dans votre engine
✅ 8 hypothèses testées automatiquement
✅ Matrice Battery Metals
✅ Évaluation contextuelle intelligente
✅ HTML enrichi avec validation
"""

import os
import re
import json
import pandas as pd
from datetime import datetime
from pathlib import Path
import subprocess
import sys
import sqlite3
import shutil
from tabulate import tabulate
import time


DIR_SCRIPTS = Path.cwd()
ONTOLOGIE_FILE = DIR_SCRIPTS / "ontologie.json"
CSV_OUTPUT = DIR_SCRIPTS / "monitoring.csv"
CSV_ENRICHED = DIR_SCRIPTS / "monitoring_enhanced.csv"
DEBUG_FILE = DIR_SCRIPTS / "debug_final_v17.txt"
VALIDATION_FILE = DIR_SCRIPTS / "validation_report.json"
HYPOTHESES_FILE = DIR_SCRIPTS / "hypotheses_check.json"
HTML_REPORT = DIR_SCRIPTS / "validation_report.html"
DATE_NOW = datetime.now().strftime("%Y-%m-%d %H:%M CET")

# Forcer UTF-8 pour Windows
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# MAPPING SCRIPT -> NODE (inchangé)
SCRIPT_TO_NODE_MAPPING = {
    "r00_zeroday.py": "R00", "r01_pboc.py": "R01", "r02_sipri.py": "R02",
    "r03_ethereum.py": "R03", "r04_usni.py": "R04", "r05_suez_canal.py": "R05",
    "r06_napoleon.py": "R06", "r07_vz_oil.py": "R07", "r09_brent.py": "R09",
    "r10_vix_cboe.py": "R10", "r11_gas_storage.py": "R11", "r12_fear_greed.py": "R12",
    "r13_opec_global.py": "R13", "r15_bitcoin.py": "R15", "r16_libya_oil.py": "R16",
    "r17_redsea_pirates.py": "R17", "r24_ttf.py": "R24", "r25_vnz_chine.py": "R25",
    "r28_seismic_m6.py": "R28", "r32_gdelt.py": "R32", "r32_17_repression.py": "R32_17",
    "r32_18_geo.py": "R32_18", "r32_20_manif.py": "R32_20", 
    "r36_usni_carriers.py": "R36", "r58_dxy.py": "R58",
    "r65_silver.py": "R65", "r65_silver_pv.py": "R65_pv", "r66_lithium.py": "R66",
    "r66_lithium_pv.py": "R66_pv", "r67_nickel.py": "R67", "r68_cobalt.py": "R68",
    "r69_graphite.py": "R69", "r70_rare_earths.py": "R70", "r71_usd1_wlfi.py": "R71",
    "r74_forets_fao.py": "R74", "r76_water.py": "R76", "r81_ioc.py": "R81",
    "r82_shadowserver.py": "R82", "r84_cereals_usda.py": "R84", "r85_soil_degradation.py": "R85",
    "r91_isc.py": "R91", "r92_dns_c2.py": "R92", "r95_ttp.py": "R95",
    "r96_hibp_breaches.py": "R96", "r97_yara_rules.py": "R97", "r98_imd_drought.py": "R98",
    "r99_moussons_imd.py": "R99", "r125_pathogenes_ecdc.py": "R125",
    "r127_niveau_mer_psmsl.py": "R127", "r200_climat_era5.py": "R200",
    "r201_energie_iea.py": "R201",
}

# COMMANDES ÉTENDUES (inchangé)
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
    "r10_vix_cboe.py": ('python -c "from r10_vix_cboe import scrape_r10; print(f\'R10 VIX={scrape_r10()}\')"', r'VIX=([\d.]+)'),
    "r11_gas_storage.py": ('python -c "from r11_gas_storage import scrape_r11; r=scrape_r11()[0]; print(f\'R11={r[\\"gas_storage_pct\\"]}% TRL9 | Fresh={r[\\"freshness_days\\"]}d | Validé={r[\\"validated_date\\"]} | {r[\\"threshold_20pct\\"]}\')"', r'R11=(\d+\.?\d*)%'),
    "r12_fear_greed.py": ('python -c "from r12_fear_greed import scrape_r12; r=scrape_r12()[0]; print(f\'R12 FGI={r[\\"fear_greed_index\\"]} | {r[\\"status\\"]}\')"', r'FGI=(\d+)'),
    "r13_opec_global.py": ('python -c "from r13_opec_global import scrape_r13; print(f\'R13 OPEC={scrape_r13()}% compliance\')"', r'OPEC=(\d+)%'),
    "r15_bitcoin.py": ('python -c "from r15_bitcoin import scrape_r15; r=scrape_r15()[0]; print(f\'R15 BTC=${r[\\"bitcoin_price_usd\\"]:,} | Δ{r[\\"change_24h_pct\\"]:+.1f}% | MC ${r[\\"market_cap_usd_t\\"]}T\')"', r'BTC=\$([\d,]+)'),
    "r16_libya_oil.py": ('python -c "from r16_libya_oil import scrape_r16; print(f\'R16 Libye={scrape_r16()} Mbpd OPEC\')"', r'Libye=(\d+\.?\d*)'),
    "r17_redsea_pirates.py": ('python -c "from r17_redsea_pirates import scrape_r17; r=scrape_r17(); print(f\'R17 RedSea={r[\\"tankers_24h\\"]} tankers/24h | Fresh=24h\')"', r'RedSea=(\d+)'),
    "r24_ttf.py": ('python -c "from r24_ttf import scrape_r24; r=scrape_r24()[0]; print(f\'R24 TTF=€{r.get(\\"ttf_gas_eur_mwh\\", \\"FAIL\\")}/MWh | {r.get(\\"status\\", \\"-\\")}\')"', r'TTF=€(\d+\.?\d*)'),
    "r25_vnz_chine.py": ('python -c "from r25_vnz_chine import scrape_r25; print(f\'R25 VZ→Chine={scrape_r25()} kbpd | Fresh=24h\')"', r'VZ→Chine=(\d+)'),
    "r28_seismic_m6.py": ('python -c "from r28_seismic_m6 import scrape_r28; print(f\'R28 M6+={scrape_r28()} événements/30j | Fresh=24h\')"', r'M6\+=(\d+)'),
    "r32_gdelt.py": ('python -c "from r32_gdelt import scrape_r32; r=scrape_r32()[0]; top3 = \\",\\".join([c[0] for c in r.get(\\"top_countries\\", [])[:3]]); print(f\'R32={r[\\"gdelt_events_18\\"]} | {r[\\"avg_tone_pts\\"]}pts | {top3}\')"', r'R32=(\d+) \| ([-\d.]+)pts \| ([^|]+)'),
    "r32_17_repression.py": ('python -c "from r32_17_repression import scrape_r32_17; print(f\'R32_17={scrape_r32_17()}\')"', r'R32_17=(.+)$'),
    "r32_18_geo.py": ('python -c "from r32_18_geo import scrape_r32_18_geo; print(f\'R32_18={scrape_r32_18_geo()}\')"', r'R32_18=(.+)$'),
    "r32_20_manif.py": ('python -c "from r32_20_manif import scrape_r32_20; print(f\'R32_20={scrape_r32_20()}\')"', r'R32_20=(.+)$'),
    "r36_usni_carriers.py": ('python -c "from r36_usni_carriers import scrape_r36; print(f\'R36 USNI={scrape_r36()}\')"', r'USNI=(\d+)'),
    "r58_dxy.py": ('python -c "from r58_dxy import scrape_r58; r=scrape_r58()[0]; print(f\'R58 DXY={r[\\"dxy_index\\"]} {r[\\"method\\"]}\')"', r'DXY=(\d+\.?\d*)'),
    "r65_silver.py": ('python -c "from r65_silver import scrape_r65; print(f\'R65 Ag=${scrape_r65()}\')"', r'Ag=\$(\d+\.\d+)'),
    "r65_silver_pv.py": ('python -c "from r65_silver_pv import scrape_r65; r=scrape_r65()[0]; print(f\'R65 Ag PV={r[\\"silver_pv_kt\\"]}kt | Total={r[\\"silver_total_kt\\"]}kt | PV={r[\\"pv_share_pct\\"]}% | Fresh={r[\\"freshness_days\\"]}d\')"', r'Ag PV=(\d+)kt'),
    "r66_lithium.py": ('python -c "from r66_lithium import scrape_r66; print(f\'R66 Li={scrape_r66()}\')"', r'Li=([\d,]+)'),
    "r66_lithium_pv.py": ('python -c "from r66_lithium_pv import scrape_r66; r=scrape_r66()[0]; print(f\'R66 Li={r[\\"lithium_mine_kt\\"]}kt | Déficit={r[\\"deficit_kt\\"]}kt | AU={r[\\"australia_kt\\"]}kt | Fresh={r[\\"fresh_days\\"]}d NON-RT\')"', r'Li=(\d+)kt'),
    "r67_nickel.py": ('python -c "from r67_nickel import scrape_r67; print(f\'R67 Ni=${scrape_r67()}\')"', r'Ni=\$(\d+)'),
    "r68_cobalt.py": ('python -c "from r68_cobalt import scrape_r68; print(f\'R68 Co=${scrape_r68()}\')"', r'Co=\$(\d+)'),
    "r69_graphite.py": ('python -c "from r69_graphite import scrape_r69; print(f\'R69 Graphite=${scrape_r69()}\')"', r'Graphite=\$(\d+)'),
    "r70_rare_earths.py": ('python -c "from r70_rare_earths import scrape_r70; print(f\'R70 RE={scrape_r70()}$/kg\')"', r'RE=(\d+)'),
    "r71_usd1_wlfi.py": ('python -c "from r71_usd1_wlfi import scrape_r71; r=scrape_r71()[0]; print(f\'R71 USD1=${r[\\"usd1_wlfi_price\\"]:.4f}\')"', r'USD1=\$(\d+\.?\d*)'),
    "r74_forets_fao.py": ('python -c "from r74_forets_fao import scrape_r74; r=scrape_r74(); print(f\'R74 Forêts={r[\\"loss_mha_yr\\"]} Mha/an | {r[\\"period\\"]} | {r[\\"validation\\"]} | Fresh={r[\\"fresh_days\\"]}j\')"', r'Forêts=(\d+\.?\d*)'),
    "r76_water.py": ('python -c "from r76_water import scrape_r76; r=scrape_r76()[0]; print(f\'R76 Eau={r[\\"water_km3\\"]}km³ | Access={r[\\"access_pct\\"]}% | Fresh={r[\\"fresh_days\\"]}d NON-RT | Stress={r[\\"stress_b\\"]}B\')"', r'Eau=(\d+)km'),
    "r81_ioc.py": ('python -c "from r81_ioc import scrape_r81; r=scrape_r81()[0]; print(f\'R81={r[\\"ioc_vt\\"]} | Fresh={r[\\"fresh_h\\"]}h | Method={r[\\"method\\"]}\')"', r'R81=(\d+)'),
    "r82_shadowserver.py": ('python -c "from r82_shadowserver import scrape_r82; print(f\'R82 CVEs={scrape_r82()}/24h\')"', r'CVEs=(\d+)'),
    "r84_cereals_usda.py": ('python -c "from r84_cereals_usda import scrape_r84; print(scrape_r84())"', r'(\d+)'),
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
    "r200_climat_era5.py": ('python -c "from r200_climat_era5 import scrape_r200; r=scrape_r200(); print(f\'R200={r[\\"final\\"]}°C | Sources={r[\\"computed\\"][\\"valid_sources\\"]} | Method={r[\\"computed\\"][\\"method\\"]} | Fresh={r[\\"fresh_h\\"]}h\')"', r'R200=([\d,]+\.?\d*)°C'),
    "r201_energie_iea.py": ('python -c "from r201_energie_iea import scrape_r201; print(f\'R201 Énergie={scrape_r201()} TWh/an | Fresh=24h\')"', r'Énergie=(\d+)'),
}

# ============================================================================
# NOUVELLES FONCTIONS DE VALIDATION ÉPISTÉMIQUE
# ============================================================================

def evaluer_statut_contextuel(node_id, valeur_num):
    """Évaluation contextuelle intelligente (logique CARTO)"""
    evaluations = {
        'R01': lambda x: '🟢 PBOC STABLE' if x > 6 else '⚠️ PBOC BAS',
        'R06': lambda x: '🟢 NAPOLÉON OK' if x > 900 else '⚠️ NAPOLÉON BAS',
        'R65': lambda x: '🟢 AG BULL' if x > 30 else '⚠️ AG BAS',
        'R25': lambda x: '🟢 CNPC VZ DOM' if x > 75 else '⚠️ CNPC BAS',
        'R12': lambda x: '🟡 PEUR' if x < 35 else '🟢 NEUTRE',
        'R57': lambda x: '🟢 BELIEF' if x < 0.75 else '⚠️ DOUTE',
        'R56': lambda x: '🟢 ACCUMULATION' if x < 3.5 else '⚠️ DISTRIBUTION',
        'R15': lambda x: '🔴 EUPHORIE' if x > 85000 else '🟢 NORMAL',
        'R67': lambda x: '🟢 Ni BULL' if x > 17000 else '⚠️ Ni BAS',
        'R68': lambda x: '🟢 Co BULL' if x > 10 else '⚠️ Co BAS',
        'R69': lambda x: '🟢 Gr BULL' if x > 600 else '⚠️ Gr BAS',
        'R70': lambda x: '🟢 REO BULL' if x > 120 else '⚠️ REO BAS',
        'R71': lambda x: '🟢 USD1 BULL' if x >= 3 else '⚠️ USD1 BAS',
        'R72': lambda x: '🟢 USDC DOM' if x >= 50 else '⚠️ USDC BAS',
        'R11': lambda x: '🚨 CRITIQUE' if x < 20 else '✅ STABLE',
        'R24': lambda x: '✅ BAS' if x < 40 else '⚠️ ÉLEVÉ',
        'R91': lambda x: '✅ BAS' if x < 100000 else '🚨 TRÈS ÉLEVÉ',
    }
    
    if node_id in evaluations:
        try:
            return evaluations[node_id](valeur_num)
        except:
            pass
    
    return '📊'  # Statut générique

def tester_hypotheses_dynamo(valeurs_dict):
    """Teste les 8 hypothèses DYNAMO v2.4"""
    hypotheses = {}
    
    # H1_P4 : LNG 15-25% ET TTF 25-50€
    r11 = valeurs_dict.get('R11', 0)
    r24 = valeurs_dict.get('R24', 0)
    hypotheses['H1_P4'] = {
        'resultat': '✅' if (40 <= r11 <= 60) and (25 <= r24 <= 50) else '❌',  
        'details': f'R11={r11}% (40-60%) | R24=€{r24} (25-50€)',
        'condition': '40% ≤ R11 ≤ 60% ET 25 ≤ R24 ≤ 50'
    }
    
    # H2_OTAN : TIV > 4000
    r02 = valeurs_dict.get('R02', 0)
    hypotheses['H2_OTAN'] = {
        'resultat': '✅' if r02 > 4000 else '❌',
        'details': f'R02={r02} > 4000',
        'condition': 'R02 (SIPRI TIV) > 4000'
    }
    
    def normalize_price(value):
        """Convertit string/float → float numérique comparable"""
        if value == '' or value is None:
            return 0.0
        
        # 1. Si déjà float → RETURN DIRECT
        if isinstance(value, (int, float)):
            return float(value)
        
        # 2. Si string → Nettoie virgules + décimales
        if isinstance(value, str):
            # Supprime espaces et virgules milliers
            clean = value.strip().replace(',', '')
            try:
                return float(clean)
            except:
                return 0.0
        
        return 0.0


    # H3_CYBER_SUPPLY CORRIGÉ
    r00 = valeurs_dict.get('R00', 0)
    r81 = valeurs_dict.get('R81', 0)
    battery_nodes = {
        'R65': 80,    # Silver $/oz > 80 BULL
        'R66': 100000, # Lithium CNY/T > 100k BULL  
        'R67': 15000,  # Nickel $/t > 15k BULL
        'R68': 40000,  # Cobalt $/lb > 40k BULL
        'R69': 450,    # Graphite $/t > 450 BULL
        'R70': 50      # RE $/kg > 50 BULL
    }

    battery_bull = sum(1 for node, seuil in battery_nodes.items() 
                      if normalize_price(valeurs_dict.get(node, '0')) > seuil)

    cyber_crit = (r00 > 15 or r81 > 500)
    hypotheses['H3_CYBER_SUPPLY'] = {
        'resultat': '✅' if cyber_crit and battery_bull >= 4 else '⚪',
        'details': f'R00={r00}(>15) R81={r81}(>500) | Battery={battery_bull}/6 | R66={valeurs_dict.get("R66","?")}',
        'condition': 'ZeroDays>15 OR IOCs>500 AND Battery>=4/6'
    }
    
    # H5_GDELT : RootCodes disponibles (simplifié)
    hypotheses['H5_GDELT'] = {
        'resultat': '✅' if valeurs_dict.get('R32', 0) > 0 else '⚠️',
        'details': f'R32={valeurs_dict.get("R32", 0)} événements',
        'condition': 'RootCodes disponibles (R32 > 0)'
    }
    
    # H6_CH_Afrique : PBOC > 45T$ ET Battery Metals bull
    r01 = valeurs_dict.get('R01', 0)
    hypotheses['H6_CH_Afrique'] = {
        'resultat': '✅' if r01 > 45 and battery_bull >= 4 else '🟡',
        'details': f'R01={r01}T$ (seuil: >45T) | Battery Bull={battery_bull}/6',
        'condition': 'PBOC > 45T$ ET Battery Metals bull'
    }
    
    # H8_CRYPTO : Fear&Greed 20-50% ET BTC 85k-100k
    r12 = valeurs_dict.get('R12', 50)
    r15_raw = valeurs_dict.get('R15', 0)

    # CORRECTION : Convertir de milliers à unités
    r15 = r15_raw * 1000 if r15_raw < 1000 else r15_raw  # Si < 1000, c'est en k$

    # DEBUG
    print(f"[DEBUG H8] R15 brut={r15_raw}, corrigé={r15}")

    fear_greed_ok = 20 <= r12 <= 50
    btc_ok = 85000 <= r15 <= 100000
        
    # H9_TECH_WAR : USD1 > 1B OU USDC > 75% ET TTPs > 5
    r71 = valeurs_dict.get('R71', 0)
    r72 = valeurs_dict.get('R72', 0)
    r95 = valeurs_dict.get('R95', 0)
    tech_war = (r71 > 1 or r72 > 75) and r95 > 5
        
        
    # H11_SCW : USD1 >= 0.9B$ (ou 1.0B selon ton choix)
    hypotheses['H11_SCW'] = {
    'resultat': '✅' if r71 >= 0.9 else '❌',  # Changé de 3.0 à 0.9
    'details': f'R71={r71}B (seuil: ≥0.9B)',
    'condition': 'USD1 ≥ 0.9B$'
}

    
    return hypotheses

def normalize_price(value):
    """Convertit string/float → float numérique"""
    if value == '' or value is None:
        return 0.0
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        clean = value.strip().replace(',', '')
        try:
            return float(clean)
        except:
            return 0.0
    return 0.0

def analyser_matrice_battery_metals(valeurs_dict):
    """Battery Metals 2026 - COMPAT HTML (avec 'bull' key)"""
    def normalize_price(value):
        if value == '' or value is None: return 0.0
        if isinstance(value, (int, float)): return float(value)
        if isinstance(value, str):
            clean = value.strip().replace(',', '')
            try: return float(clean)
            except: return 0.0
        return 0.0

    battery_nodes = {
        'R65': {'nom': 'Silver', 'seuil': 80, 'unite': '$/oz'},      
        'R66': {'nom': 'Lithium', 'seuil': 100000, 'unite': 'CNY/T'}, 
        'R67': {'nom': 'Nickel', 'seuil': 15000, 'unite': '$/t'},     
        'R68': {'nom': 'Cobalt', 'seuil': 40000, 'unite': '$/lb'},    
        'R69': {'nom': 'Graphite', 'seuil': 450, 'unite': '$/t'},     
        'R70': {'nom': 'Rare Earths', 'seuil': 50, 'unite': '$/kg'}   
    }
    
    resultats = {}
    bull_count = 0
    
    for node_id, info in battery_nodes.items():
        valeur = normalize_price(valeurs_dict.get(node_id, 0))
        is_bull = valeur > info['seuil']
        statut = '🟢 BULL' if is_bull else '🟡 NEUTRE'
        
        if is_bull:
            bull_count += 1
            
        resultats[node_id] = {
            'metal': info['nom'],
            'valeur': f"{valeur:.0f}",
            'seuil': info['seuil'],
            'unite': info['unite'],
            'statut': statut,
            'bull': is_bull  # ← CLÉ REQUISE PAR HTML
        }
    
    if bull_count >= 4:
        supercycle = '🟢 SUPERCYCLE'
        recommandation = '🚀 ACCUMULATION AGRESSIVE'
    elif bull_count >= 3:
        supercycle = '🟡 BULLE'
        recommandation = '📈 SURVEILLANCE AGRESSIVE'
    else:
        supercycle = '🔴 FAIBLE'
        recommandation = '⏳ ATTENTE'
    
    return {
        'details': resultats,
        'bull_count': bull_count,
        'total': len(battery_nodes),
        'supercycle': supercycle,
        'recommandation': recommandation
    }



def calculer_idd(hypotheses_resultats):
    """Calcule l'Indice de Décision Dynamique"""
    # Convertir en format simplifié pour le calcul
    scores = {'✅': 1, '🟢': 1, '🟡': 0.5, '⚠️': 0.5, '⚪': 0.25, '❌': 0}
    
    total_score = 0
    for hyp_id, data in hypotheses_resultats.items():
        resultat = data['resultat']
        total_score += scores.get(resultat, 0)
    
    # Score IDD (0-100)
    idd_score = (total_score / len(hypotheses_resultats)) * 100 if hypotheses_resultats else 0
    
    # Niveau de décision
    if idd_score >= 75:
        decision = "🟢 ROUTINE OK"
        description = "Toutes conditions favorables"
    elif idd_score >= 50:
        decision = "🟡 SURVEILLANCE"
        description = "Conditions mitigées, vigilance requise"
    else:
        decision = "🔴 RELANCER"
        description = "Conditions défavorables, action requise"
    
    return {
        'score': round(idd_score, 1),
        'decision': decision,
        'description': description,
        'hypotheses_evaluees': len(hypotheses_resultats)
    }

def generer_rapport_html(valeurs_dict, hypotheses, battery_matrix, idd, donnees_enhanced):
    """Génère un rapport HTML enrichi avec validation"""
    
    # Calculer les statistiques pour le footer
    total_numeriques = sum(1 for _, row in donnees_enhanced.items() 
                          if str(row['valeur_live']).replace('.', '').replace(',', '').isdigit())
    total_nodes = len(donnees_enhanced)
    hyp_ok = sum(1 for _, data in hypotheses.items() if data['resultat'] in ['✅', '🟢'])
    total_hyp = len(hypotheses)
    battery_bull = battery_matrix['bull_count']
    
    global_status = "🟢 OPTIMAL" if idd['score'] >= 75 else "🟡 MODÉRÉ" if idd['score'] >= 50 else "🔴 CRITIQUE"
    global_class = "✅" if idd['score'] >= 75 else "⚠️" if idd['score'] >= 50 else "🚨"
    
    html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Rxx Engine V17.0 - Validation Épistémique</title>
    <style>
        body {{ font-family: 'Segoe UI', Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1400px; margin: 0 auto; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 10px; margin-bottom: 20px; }}
        .card {{ background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); margin-bottom: 20px; }}
        .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }}
        table {{ width: 100%; border-collapse: collapse; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #f2f2f2; }}
        .🔴 {{ background-color: #ffcccc; }}
        .🟡 {{ background-color: #ffffcc; }}
        .🟢 {{ background-color: #ccffcc; }}
        .🚨 {{ color: #d32f2f; font-weight: bold; }}
        .✅ {{ color: #388e3c; }}
        .⚠️ {{ color: #f57c00; }}
        .📊 {{ color: #1976d2; }}
        .hypothesis {{ padding: 10px; margin: 5px 0; border-left: 4px solid; }}
        .hyp-ok {{ border-left-color: #4caf50; background: #e8f5e9; }}
        .hyp-warn {{ border-left-color: #ff9800; background: #fff3e0; }}
        .hyp-ko {{ border-left-color: #f44336; background: #ffebee; }}
        .idd-score {{ font-size: 48px; font-weight: bold; text-align: center; margin: 20px 0; }}
        .idd-ok {{ color: #4caf50; }}
        .idd-warn {{ color: #ff9800; }}
        .idd-ko {{ color: #f44336; }}
        .battery-metal {{ display: inline-block; padding: 5px 10px; margin: 2px; border-radius: 4px; }}
        .battery-bull {{ background: #4caf50; color: white; }}
        .battery-bear {{ background: #f44336; color: white; }}
        .timestamp {{ color: #666; font-size: 0.9em; }}
            /* ⬇️ AJOUTEZ ICI LES NOUVEAUX STYLES GDELT ⬇️ */
        .highlight {{ font-weight: bold; background-color: #e3f2fd; }}
        .negative {{ color: #d32f2f; font-weight: bold; }}
        .positive {{ color: #388e3c; font-weight: bold; }}
        .neutral {{ color: #666; }}
        .gdelt-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 15px; margin-top: 15px; }}
        .gdelt-card {{ background: white; border-radius: 8px; padding: 15px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); border-left: 4px solid #2196f3; }}
        .gdelt-metric {{ margin: 8px 0; display: flex; justify-content: space-between; }}
        .gdelt-metric .label {{ font-weight: 600; color: #555; }}
        .gdelt-metric .value {{ font-weight: bold; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 Rxx Engine V17.0 - Validation Épistémique Intégrée</h1>
            <p class="timestamp">Généré le: {DATE_NOW}</p>
            <p>Intelligence CARTO/DYNAMO intégrée | 8 hypothèses testées | Matrice Battery Metals</p>
        </div>
        
        <div class="grid">
            <div class="card">
                <h2>📈 Indice de Décision Dynamique (IDD)</h2>
                <div class="idd-score {'idd-ok' if idd['score'] >= 75 else 'idd-warn' if idd['score'] >= 50 else 'idd-ko'}">
                    {idd['score']}/100
                </div>
                <h3>{idd['decision']}</h3>
                <p>{idd['description']}</p>
                <p>Basé sur {idd['hypotheses_evaluees']} hypothèses évaluées</p>
            </div>
            
            <div class="card">
                <h2>⚡ Matrice Battery Metals</h2>
                <p><strong>{battery_matrix['bull_count']}/6 en bull market</strong> - {battery_matrix['supercycle']}</p>
                <p><strong>Recommandation:</strong> {battery_matrix['recommandation']}</p>
                <div>
"""
    
    # Afficher les métaux
    for node_id, metal_info in battery_matrix['details'].items():
        bull_class = "battery-bull" if metal_info['bull'] else "battery-bear"
        html_content += f"""
                    <span class="battery-metal {bull_class}">
                        {metal_info['metal']}: {metal_info['valeur']}{metal_info['unite']}
                    </span>
"""
    
    html_content += f"""
                </div>
            </div>
        </div>
        
        <div class="card">
            <h2>🔍 Hypothèses DYNAMO v2.4</h2>
"""
    
    # Afficher les hypothèses
    for hyp_id, data in hypotheses.items():
        css_class = "hyp-ok" if data['resultat'] in ['✅', '🟢'] else "hyp-warn" if data['resultat'] in ['⚠️', '🟡', '⚪'] else "hyp-ko"
        html_content += f"""
            <div class="hypothesis {css_class}">
                <strong>{hyp_id}: {data['resultat']}</strong><br>
                {data['details']}<br>
                <small>{data['condition']}</small>
            </div>
"""
    
    html_content += f"""
        </div>
        
        <div class="card">
            <h2>🎯 Valeurs Critiques avec Évaluation Contextuelle</h2>
            <table>
                <tr>
                    <th>Nœud</th>
                    <th>Valeur</th>
                    <th>Statut</th>
                    <th>Évaluation</th>
                    <th>Hypothèse</th>
                </tr>
"""
    
            
    # Nœuds critiques avec évaluation
    nodes_critiques = ['R00', 'R01', 'R02', 'R11', 'R15', 'R24', 'R81', 'R91', 'R65', 'R71']
    for node_id in nodes_critiques:
        if node_id in donnees_enhanced:
            row = donnees_enhanced[node_id]
            html_content += f"""
                <tr>
                    <td><strong>{row['node_id']}</strong></td>
                    <td>{row['valeur_live']}</td>
                    <td>{row['statut_contextuel']}</td>
                    <td>{row['alerte_seuil']}</td>
                    <td>{row['hypothese_liee']}</td>
                </tr>
"""
    
    html_content += f"""
            </table>
        </div>
        
        <div class="card">
            <h2>📋 Statistiques Générales</h2>
            <p><strong>Valeurs numériques extraites:</strong> {total_numeriques}/{total_nodes}</p>
            <p><strong>Hypothèses validées:</strong> {hyp_ok}/{total_hyp}</p>
            <p><strong>Battery Metals en bull:</strong> {battery_bull}/6</p>
            <p><strong>Statut global:</strong> <span class="{global_class}">{global_status}</span></p>
        </div>
        
        <div class="timestamp">
            <p>Rxx Engine V17.0 - Intelligence épistémique intégrée</p>
            <p>Données temps réel + Validation CARTO/DYNAMO</p>
        </div>
    </div>
</body>
</html>
"""
    
    with open(HTML_REPORT, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    return HTML_REPORT

# ============================================================================
# FONCTIONS EXISTANTES AVEC AMÉLIORATIONS
# ============================================================================

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
        
        if result.returncode == 0 and output:
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
    
    cleaned = output.strip()
    
    # Pattern spécifique
    if script_name in COMMANDES_ETENDUES:
        _, pattern = COMMANDES_ETENDUES[script_name]
        match = re.search(pattern, cleaned)
        if match:
            valeur = match.group(1)
            valeur = valeur.replace(',', '.').replace(',', '')
            debug_log(f"  ✓ Pattern étendu: {valeur}")
            return valeur
    
    # Patterns génériques
    patterns_generiques = [
        r'R\d+\s*=\s*([\d,.]+)',
        r'=\s*([\d,.]+)[\s|]',
        r'([\d,.]+)\s*[°%€$]',
        r'(\d+[,.]?\d*)\s*(?:T|M|k|m|%|°|€|\$)',
    ]
    
    for pattern in patterns_generiques:
        match = re.search(pattern, cleaned)
        if match:
            valeur = match.group(1)
            valeur = valeur.replace(',', '.').replace(',', '')
            debug_log(f"  ✓ Pattern générique: {valeur}")
            return valeur
    
    # Dernier recours
    match = re.search(r'(\d+[,.]?\d*)', cleaned)
    if match:
        valeur = match.group(1)
        valeur = valeur.replace(',', '.')
        debug_log(f"  ✓ Nombre trouvé: {valeur}")
        return valeur
    
    debug_log(f"  ✗ Aucune valeur numérique trouvée")
    return cleaned[:50]

def analyser_seuil(seuil_str):
    """Analyse un seuil pour extraire valeur et unité"""
    if not seuil_str:
        return None, None, None
    
    seuil_str = str(seuil_str).strip()
    
    patterns = [
        (r'>\s*(\d+\.?\d*)\s*(k|K|M|B|T)?', '>'),
        (r'<\s*(\d+\.?\d*)\s*(k|K|M|B|T)?', '<'),
        (r'(\d+\.?\d*)\s*(k|K|M|B|T)?', '='),
    ]
    
    for pattern, operator in patterns:
        match = re.search(pattern, seuil_str)
        if match:
            valeur = float(match.group(1))
            unité = match.group(2) if match.group(2) else ''
            return valeur, unité, operator
    
    return None, None, None

def comparer_valeur_seuil(valeur_str, seuil_str, node_id):
    """Compare une valeur avec un seuil, gère les unités"""
    try:
        valeur_clean = str(valeur_str).replace(',', '.').replace(' ', '')
        
        try:
            valeur_num = float(valeur_clean)
        except:
            return "📊"
        
        seuil_val, unité, operator = analyser_seuil(seuil_str)
        if not seuil_val:
            return "📊"
        
        facteurs = {
            'k': 1000, 'K': 1000,
            'M': 1000000,
            'B': 1000000000,
            'T': 1000000000000
        }
        
        if unité in facteurs:
            seuil_converti = seuil_val * facteurs[unité]
        else:
            seuil_converti = seuil_val
        
        if operator == '>':
            return "🚨" if valeur_num > seuil_converti else "✅"
        elif operator == '<':
            return "🚨" if valeur_num < seuil_converti else "✅"
        else:
            return "🚨" if valeur_num >= seuil_converti else "✅"
            
    except Exception as e:
        debug_log(f"⚠️  Erreur comparaison {node_id}: {e}")
        return "⚠️"

def determiner_hypothese_liee(node_id):
    """Détermine quelle hypothèse DYNAMO est liée à ce nœud"""
    mapping = {
        'R00': 'H3_CYBER_SUPPLY',
        'R01': 'H6_CH_Afrique',
        'R02': 'H2_OTAN',
        'R11': 'H1_P4',
        'R15': 'H8_CRYPTO',
        'R24': 'H1_P4',
        'R32': 'H5_GDELT',
        'R65': 'H3_CYBER_SUPPLY',
        'R66': 'H3_CYBER_SUPPLY',
        'R67': 'H3_CYBER_SUPPLY',
        'R68': 'H3_CYBER_SUPPLY',
        'R69': 'H3_CYBER_SUPPLY',
        'R70': 'H3_CYBER_SUPPLY',
        'R71': 'H9_TECH_WAR',
        'R72': 'H9_TECH_WAR',
        'R81': 'H3_CYBER_SUPPLY',
        'R95': 'H9_TECH_WAR',
    }
    
    return mapping.get(node_id, '')

# ============================================================================
# FONCTION PRINCIPALE
# ============================================================================

def main():
    """Méthode principale V17.0 avec validation épistémique intégrée"""
    # Nettoyer les anciens fichiers de debug
    if DEBUG_FILE.exists():
        DEBUG_FILE.unlink()
    
    debug_log(f"🚀 ENGINE V17.0 - Démarrage {DATE_NOW}")
    
    import time  # AJOUTER CET IMPORT ICI
    
    # ⏱️ Début du timing global
    execution_start_time = time.perf_counter()
    
    print(f"\n{'='*80}")
    print(f"🚀 Rxx Engine V17.0 - VALIDATION ÉPISTÉMIQUE INTÉGRÉE")
    print(f"📅 {DATE_NOW}")
    print(f"{'='*80}")
    
    # Charger ontologie
    try:
        with open(ONTOLOGIE_FILE, 'r', encoding='utf-8') as f:
            ontologie = json.load(f)
        nodes = ontologie.get("noeuds", {})
        print(f"📁 Ontologie: {len(nodes)} nœuds chargés")
    except Exception as e:
        print(f"❌ Erreur ontologie: {e}")
        nodes = {}
    
    # Exécuter les scripts
    donnees_live = {}
    valeurs_numeriques = {}  # Pour les analyses


   
    # ============================================================================
    # EXECUTION DES SCRIPTS
    # ============================================================================
    print(f"\n⚡ EXÉCUTION DES SCRIPTS:")   
    # ⚠️ AJOUTER CES 6 LIGNES CRITIQUES ⚠️
    L_NODE = 10      # "▶️ R00" 
    L_PRIO = 3       # "🔴" 
    L_DOM = 12       # "CYBER" 
    L_SCRIPT = 20    # "r00_zeroday.py" 
    L_DATA = 35      # Donnée description
    L_STATUS = 12    # "[OK        ]"


    for script_name, node_id in sorted(SCRIPT_TO_NODE_MAPPING.items()):
        if not Path(script_name).exists():
            # ❌ R00       🔴 CYBER      r00_zeroday.py  Zero-Days CVE (CISA/NVD)       [SCRIPT_MISS] → 
            print(f"  ❌ {node_id:<{L_NODE-2}} ", end="")
            print(f"{'🔴':<{L_PRIO}} ", end="")
            print(f"{'N/A':<{L_DOM}} ", end="")
            print(f"{script_name:<{L_SCRIPT}} ", end="")
            print(f"{'SCRIPT MANQUANT':<{L_DATA}} ", end="")
            print(f"[{'SCRIPT_MISS':<{L_STATUS-2}}] → ")
            
            donnees_live[node_id] = {
                "valeur": "SCRIPT_MISSING", 
                "statut": "NO_FILE", 
                "output": "",
                "duration": 0.0
            }
            continue
        
        node_info = nodes.get(node_id, {})
        priorite = node_info.get("priorite", "🟡")
        domaine = node_info.get("domaine", "")
        script_display = node_info.get("script", "")[:L_SCRIPT]
        donnee = node_info.get("donnee", "")[:L_DATA]
        
        # AFFICHAGE IMMÉDIAT (temps réel)
        print(f"  ▶️  {node_id:<{L_NODE-4}}\t ", end="", flush=True)
        print(f"{priorite:<{L_PRIO}} ", end="", flush=True)
        print(f"{domaine:<{L_DOM}} ", end="", flush=True)
        print(f"{script_display:<{L_SCRIPT}} ", end="", flush=True)
        print(f"{donnee:<{L_DATA}} ", end="", flush=True)
        
        # ⏱️ DÉBUT TIMING SCRIPT (JUSTE avant l'exécution)
        script_start_time = time.perf_counter()
        
        # EXÉCUTION (temps réel)
        statut, output = executer_commande_etendue(script_name, node_id)
        
        # ⏱️ FIN TIMING SCRIPT (JUSTE après l'exécution)
        script_end_time = time.perf_counter()
        script_duration = script_end_time - script_start_time
        
        valeur = extraire_valeur_etendue(output, node_id, script_name)
        
        # AFFICHER LE RÉSULTAT AVEC DURÉE
        print(f"[{statut:<{L_STATUS-2}}] → {valeur}\t\t ({script_duration:.2f}s)", flush=True)
        
        # Stocker (pour plus tard)
        donnees_live[node_id] = {
            "valeur": valeur,
            "statut": statut,
            "script": script_name,
            "output": output[:100],
            "duration": script_duration  # ⏱️ DURÉE RÉELLE
        }
        
        # Extraire valeur numérique
        try:
            val_clean = valeur.replace(',', '.').replace(' ', '')
            if re.match(r'^-?\d+\.?\d*$', val_clean):
                valeurs_numeriques[node_id] = float(val_clean)
        except:
            valeurs_numeriques[node_id] = 0

        if node_id.startswith('R32_'):
            # Pour GDELT, afficher la sortie complète au lieu de la valeur extraite
            valeur_pour_affichage = output  # ou cleaned
        else:
            valeur_pour_affichage = valeur
    # ============================================================================
    # VALIDATION ÉPISTÉMIQUE
    # ============================================================================
    print(f"\n🔬 VALIDATION ÉPISTÉMIQUE:")
    print(f"{'-'*80}")
    
    # 1. Tester les hypothèses DYNAMO
    print("📊 Test des 8 hypothèses DYNAMO v2.4:")
    hypotheses = tester_hypotheses_dynamo(valeurs_numeriques)
    for hyp_id, data in hypotheses.items():
        print(f"  {data['resultat']} {hyp_id}: {data['details']}")
    
    # 2. Analyser la matrice Battery Metals
    print(f"\n🔋 Analyse Matrice Battery Metals:")
    battery_matrix = analyser_matrice_battery_metals(valeurs_numeriques)
    print(f"  {battery_matrix['bull_count']}/6 en bull market → {battery_matrix['supercycle']}")
    print(f"  Recommandation: {battery_matrix['recommandation']}")
    
    # 3. Calculer l'IDD
    idd = calculer_idd(hypotheses)
    print(f"\n🎯 Indice de Décision Dynamique (IDD):")
    print(f"  Score: {idd['score']}/100")
    print(f"  Décision: {idd['decision']}")
    print(f"  {idd['description']}")
    
    # ============================================================================
    # GÉNÉRATION DES FICHIERS ENRICHIS
    # ============================================================================
    
    # 1. Générer CSV enrichi avec validation
    print(f"\n📊 GÉNÉRATION DES RAPPORTS:")
    
    donnees_enhanced = {}
    rows = []
    
    for node_id, node in nodes.items():
        live = donnees_live.get(node_id, {})
        valeur_live = live.get("valeur", node.get("valeur_live", "MANUEL"))
        
        # Évaluation contextuelle
        try:
            val_num = float(str(valeur_live).replace(',', '.'))
            statut_contextuel = evaluer_statut_contextuel(node_id, val_num)
        except:
            statut_contextuel = "📊"
        
        # Alerte seuil
        seuil = node.get("seuil", "")
        alerte_seuil = comparer_valeur_seuil(valeur_live, seuil, node_id)
        
        # Hypothèse liée
        hypothese_liee = determiner_hypothese_liee(node_id)
        
        row = {
            "node_id": node_id,
            "donnee": node.get("donnee", ""),
            "domaine": node.get("domaine", ""),
            "priorite": node.get("priorite", ""),
            "valeur_live": valeur_live,
            "statut_contextuel": statut_contextuel,
            "alerte_seuil": alerte_seuil,
            "hypothese_liee": hypothese_liee,
            "statut_exec": live.get("statut", "MANUEL"),
            "seuil": seuil,
            "timestamp": DATE_NOW
        }
        
        rows.append(row)
        donnees_enhanced[node_id] = row
    
    # DataFrame enrichi
    df_enhanced = pd.DataFrame(rows)
    priority_order = {"🔴": 0, "🟡": 1, "🟢": 2, "": 3}
    df_enhanced['priority_num'] = df_enhanced['priorite'].map(priority_order)
    df_enhanced = df_enhanced.sort_values(['priority_num', 'domaine', 'node_id'])
    df_enhanced = df_enhanced.drop('priority_num', axis=1)
    
    # Sauvegarder CSV enrichi
    df_enhanced.to_csv(CSV_ENRICHED, index=False, sep=';', encoding='utf-8')
    print(f"  ✓ monitoring_enhanced.csv généré ({len(rows)} lignes)")
    
    # 2. Générer rapport JSON des hypothèses
    rapport_complet = {
        'metadata': {
            'version': 'Rxx Engine V17.0',
            'date': DATE_NOW,
            'validation_type': 'ÉPISTÉMIQUE_INTÉGRÉE'
        },
        'idd': idd,
        'hypotheses': hypotheses,
        'battery_metals': battery_matrix,
        'valeurs_critiques': {node_id: valeurs_numeriques.get(node_id, 0) 
                             for node_id in ['R00', 'R01', 'R02', 'R11', 'R15', 'R24', 'R81', 'R91']},
        'statistiques': {
            'total_valeurs': len(donnees_live),
            'valeurs_numeriques': len(valeurs_numeriques),
            'hypotheses_ok': sum(1 for h in hypotheses.values() if h['resultat'] in ['✅', '🟢']),
            'battery_bull': battery_matrix['bull_count']
        }
    }
    
    with open(VALIDATION_FILE, 'w', encoding='utf-8') as f:
        json.dump(rapport_complet, f, indent=2, ensure_ascii=False)
    print(f"  ✓ validation_report.json généré")
    
    # 3. Générer fichier hypothèses dédié
    with open(HYPOTHESES_FILE, 'w', encoding='utf-8') as f:
        json.dump(hypotheses, f, indent=2, ensure_ascii=False)
    print(f"  ✓ hypotheses_check.json généré")
    
    # 4. Générer rapport HTML
    html_file = generer_rapport_html(valeurs_numeriques, hypotheses, battery_matrix, idd, donnees_enhanced)
    print(f"  ✓ validation_report.html généré (ouvrez dans navigateur)")
    
        # ============================================================================
    # INTÉGRATION BASE DE DONNÉES CHRONOLOGIQUE - VERSION CORRIGÉE
    # ============================================================================
    print(f"\n💾 INTÉGRATION BASE DE DONNÉES CHRONOLOGIQUE:")
    
    try:
        # Importer et exécuter simplement
        from db_integration import integrate_with_engine_v17
        
        print("   📦 Module db_integration trouvé...")
        
        # Exécuter l'intégration (ignorer le type de retour)
        result = integrate_with_engine_v17()
        
        if result is not None:
            print("   ✅ Données stockées avec succès")
            
            # Extraire l'ID d'exécution selon le format
            exec_id = None
            if isinstance(result, dict):
                if 'execution_id' in result:
                    exec_id = result['execution_id']
                elif 'db' in result and hasattr(result['db'], '_generate_execution_id'):
                    # Alternative: générer un nouvel ID
                    from datetime import datetime
                    exec_id = result['db']._generate_execution_id(datetime.now())
            
            # Afficher les statistiques
            try:
                import sqlite3
                conn = sqlite3.connect("rxx_history.db")
                cursor = conn.cursor()
                
                # Nombre d'exécutions
                count = cursor.execute("SELECT COUNT(*) FROM executions").fetchone()[0]
                
                # Dernière exécution
                last = cursor.execute("""
                    SELECT execution_id, start_time, idd_score, total_nodes 
                    FROM executions 
                    ORDER BY start_time DESC 
                    LIMIT 1
                """).fetchone()
                
                conn.close()
                
                print(f"   📊 Base : rxx_history.db ({count} exécutions)")
                if last:
                    print(f"   🎯 Dernière : {last[0]}")
                    print(f"   📈 IDD: {last[2]:.1f} | Nœuds: {last[3]}")
                    
            except sqlite3.Error:
                print(f"   📊 Base : rxx_history.db (statistiques non disponibles)")
        else:
            print("   ⚠️  Intégration retournée None (erreur silencieuse)")
            
    except ImportError as e:
        print(f"   ⚠️  Module db_integration non disponible: {e}")
    except Exception as e:
        print(f"   ❌ Erreur d'intégration : {str(e)[:80]}")


    
    # ============================================================================
    # AFFICHAGE DES RÉSULTATS
    # ============================================================================
    
    print(f"\n📈 STATISTIQUES V17.0:")
    print(f"   Nœuds totaux: {len(nodes)}")
    print(f"   Scripts exécutés: {len([v for v in donnees_live.values() if v['statut'] not in ['MANUEL', 'NO_FILE']])}")
    print(f"   Valeurs numériques: {len(valeurs_numeriques)}")
    print(f"   Hypothèses validées: {rapport_complet['statistiques']['hypotheses_ok']}/8")
    print(f"   Battery Metals en bull: {battery_matrix['bull_count']}/6")
    print(f"   IDD Score: {idd['score']}/100 → {idd['decision']}")    
    print(f"\n📁 FICHIERS GÉNÉRÉS:")
    print(f"   {CSV_ENRICHED} - Données enrichies avec validation")
    print(f"   {VALIDATION_FILE} - Rapport complet de validation")
    print(f"   {HYPOTHESES_FILE} - Résultats des 8 hypothèses")
    print(f"   {html_file} - Dashboard HTML interactif")
    print(f"   {DEBUG_FILE} - Logs détaillés")
    
    # DASHBOARD PRIORITAIRE AVEC VALIDATION
    print(f"\n🎯 DASHBOARD PRIORITAIRE AVEC VALIDATION:")
    print("="*100)
    
    # Filtrer les priorités 🔴
    prioritaires = df_enhanced[df_enhanced["priorite"] == "🔴"][["node_id", "valeur_live", "statut_contextuel", "alerte_seuil", "hypothese_liee"]]
    
    for idx, row in prioritaires.iterrows():
        hyp_info = f"[{row['hypothese_liee']}]" if row['hypothese_liee'] else ""
        print(f"{row['alerte_seuil']} {row['node_id']:>6} {str(row['valeur_live']):>12} {row['statut_contextuel']:>20} {hyp_info}")
    
    print("="*100)
    
    # AFFICHAGE DES RÉSULTATS DE VALIDATION
    print(f"\n🔬 SYNTHÈSE DE VALIDATION:")
    print(f"   IDD: {idd['score']}/100 → {idd['decision']}")
    print(f"   Battery Metals: {battery_matrix['bull_count']}/6 en bull → {battery_matrix['supercycle']}")
    
    hyp_status = []
    for hyp_id, data in hypotheses.items():
        hyp_status.append(f"{hyp_id}:{data['resultat']}")
    
    print(f"   Hypothèses: {' '.join(hyp_status)}")
    
    # ============================================================================
    # TIMING FINAL
    # ============================================================================
    execution_end_time = time.perf_counter()
    total_duration = execution_end_time - execution_start_time
    
    print(f"\n⏱️  TIMING D'EXÉCUTION:")
    print(f"   Durée totale: {total_duration:.2f}s")
    
    # Afficher les 5 scripts les plus lents
    slow_scripts = []
    for node_id, data in donnees_live.items():
        if 'duration' in data:
            slow_scripts.append((node_id, data['duration']))
    
    slow_scripts.sort(key=lambda x: x[1], reverse=True)
    if slow_scripts:
        print(f"   Scripts les plus lents:")
        for node_id, duration in slow_scripts[:5]:
            print(f"     {node_id}: {duration:.2f}s")
    else:
        print(f"   ⚠️  Aucun timing de script disponible")
        
    # RECOMMANDATIONS FINALES
    print(f"\n💡 RECOMMANDATIONS V17.0:")
    if idd['score'] >= 75:
        print(f"   ✅ ENVIRONNEMENT OPTIMAL - Continuer le monitoring normal")
    elif idd['score'] >= 50:
        print(f"   ⚠️  VIGILANCE REQUISE - Surveiller les indicateurs critiques")
    else:
        print(f"   🔴 ACTION REQUISE - Revoir les hypothèses et stratégies")
    
    if battery_matrix['bull_count'] >= 4:
        print(f"   🔋 SUPERCYCLE BATTERY METALS - Opportunité d'accumulation")
    
    # À la fin de main(), juste avant les derniers print :




if __name__ == "__main__":
    main()
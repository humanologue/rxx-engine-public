# r99_moussons_imd.py - IMD India SW Monsoon 2026 Forecast V9 FULL TRACE
import requests
import re
from datetime import datetime

def scrape_r99():
    """R99: IMD SW Monsoon India 2026 %LPA FULL TRACE V9"""
    sources = {
        'IMD_LRF_April': {
            'url': 'https://mausam.imd.gov.in/responsive/monsooninformation.php',
            'pattern': r'(?:monsoon|SWM).*?(\d{3})?\s*%?\s*(?:LPA|normal)',
            'metric': 'sw_monsoon_pct_lpa'
        },
        'IMD_Seasonal': {
            'url': 'https://internal.imd.gov.in/pages/press_release_mausam.php',
            'pattern': r'(\d{3})?\s*%?\s*LPA.*?monsoon',
            'metric': 'seasonal_forecast'
        },
        'IMD_MMCFS': {
            'url': 'https://www.imdpune.gov.in/clim_pred/lrf_bull/imp_bull.html',
            'pattern': r'(?:above|normal|below).*monsoon.*?(\d+\.?\d*)?',
            'metric': 'mmcfs_model'
        }
    }
    
    monsoon_data = []
    metadata = {'sources': {}, 'computed': {}, 'final': 0}
    
    for name, config in sources.items():
        try:
            r = requests.get(config['url'], timeout=15)
            if r.status_code == 200:
                matches = re.findall(config['pattern'], r.text, re.I)
                if matches:
                    pct_str = matches[0].strip('%')
                    pct = float(pct_str) if pct_str else 100.0
                    monsoon_data.append({
                        'source': name, 
                        'value': pct,
                        'timestamp': datetime.now().isoformat()
                    })
                    metadata['sources'][name] = True
        except Exception as e:
            print(f"❌ {name}: {e}")
            continue

    # Calcul final LPA %
    if monsoon_data:
        final_pct = sum(d['value'] for d in monsoon_data) / len(monsoon_data)
        metadata['computed'] = {
            'valid_sources': len(monsoon_data),
            'method': 'imd_monsoon_avg',
            'raw_values': [d['value'] for d in monsoon_data]
        }
    else:
        final_pct = 100.0
        metadata['computed'] = {'valid_sources': 0, 'method': 'default_normal'}

    return {
        'final_pct': round(final_pct, 1),
        'computed': metadata['computed'],
        'fresh_h': 24,
        'sources': metadata['sources']
    }

if __name__ == "__main__":
    result = scrape_r99()
    print(f"R99={result['final_pct']}% LPA | Sources={result['computed']['valid_sources']}")


# find_bug_patterns.py
import re

def find_bug_patterns_in_file(file_path):
    """Trouve tous les bugs de formatage ? dans le fichier"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Pattern pour trouver les strings avec ? bizarre
    pattern = r'f?\'[^\']*\(\?[^\']*\''
    bugs = re.findall(pattern, content)
    
    print(f"🔍 Recherche de bugs dans {file_path}")
    print("="*60)
    
    if bugs:
        print(f"❌ {len(bugs)} bugs trouvés :")
        for i, bug in enumerate(bugs[:10], 1):  # Affiche les 10 premiers
            print(f"  {i}. {bug[:100]}...")
        
        # Recherche spécifique des hypothèses
        print(f"\n🔎 Recherche spécifique par hypothèse :")
        
        hypotheses_patterns = {
            'H3_CYBER_SUPPLY': [r'>15\?', r'>500\?'],
            'H6_CH_Afrique': [r'>45T\?'],
            'H8_CRYPTO': [r'20-40\?', r'85k-95k\?'],
            'H9_TECH_WAR': [r'>2B\?', r'>75%\?', r'>5\?'],
            'H11_SCW': [r'≥3B\?']
        }
        
        for hyp_name, patterns in hypotheses_patterns.items():
            for pattern in patterns:
                matches = re.findall(pattern, content)
                if matches:
                    print(f"  {hyp_name}: {pattern} → {len(matches)} occurence(s)")
    else:
        print("✅ Aucun bug trouvé !")
    
    return bugs

if __name__ == "__main__":
    find_bug_patterns_in_file("Rxx_Engine_V17.0.py")
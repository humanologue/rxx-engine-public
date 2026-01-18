## 🔑 Configuration Credentials - USAGE SÉCURISÉ

### **⚠️ AVERTISSEMENT CRITIQUE**
Ce dépôt contient des **placeholders** uniquement. Les vraies clés API restent **locales**.

✅ API_KEY="agsi_api_key" → REMPLACER par votre clé AGSI
✅ PASSWORD="password" → REMPLACER par votre mot de passe ACLED
✅ eng-serenity-*.json → .gitignore (fichiers locaux NON trackés)

text

### **📋 .env.example (Créer ce fichier)**

```env
# .env.example - COPIER en .env pour vos clés réelles
AGSI_API_KEY=votre_clé_agsi_ici
ACLED_EMAIL=votre@email.com
ACLED_PASSWORD=votre_mot_de_passe
SERENITY_KEY=votre_clé_serenity
TELEGRAM_BOT_TOKEN=votre_token_telegram
TELEGRAM_CHAT_ID=votre_chat_id

🎛️ Activation Automatique (dans le code)

python
# r11_gas_storage.py, r33_gdelt19_acled.py
import os
from dotenv import load_dotenv

load_dotenv()  # Charge .env automatiquement

API_KEY = os.getenv("AGSI_API_KEY") or "agsi_api_key"
PASSWORD = os.getenv("ACLED_PASSWORD") or "password"

✅ Structure Sécurisée

text
rxx-engine/
├── .gitignore          ✅ eng-serenity-*.json
├── .env.example        ✅ Template (tracké)
├── .env                ✅ Vos clés (NON tracké → .gitignore)
├── db_local/           ✅ .gitignore (NON tracké)
├── cache/              ✅ .gitignore (NON tracké)
└── Rxx_Engine_V17.2.py ✅ Placeholders safe

🚀 Routine Déploiement (2min)

bash
git clone https://codeberg.org/humanologue/rxx-engine.git
cd rxx-engine
cp .env.example .env
# Éditez .env avec VOS clés
pip install -r requirements.txt python-dotenv
python Rxx_Engine_V17.2.py
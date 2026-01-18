# telegram_alerts.py
import requests
import json
from datetime import datetime

class TelegramAlerter:
    def __init__(self, bot_token="", chat_id=""):
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.enabled = bool(bot_token and chat_id)
    
    def send_idd_alert(self, idd_score, hypotheses_status):
        if not self.enabled:
            return
        
        # Déterminer le niveau d'alerte
        if idd_score >= 75:
            emoji, level = "🟢", "OPTIMAL"
            notify = False
        elif idd_score >= 50:
            emoji, level = "🟡", "SURVEILLANCE"
            notify = True
        else:
            emoji, level = "🔴", "ALERTE CRITIQUE"
            notify = True
        
        # Compter les hypothèses validées
        valid_count = sum(1 for h in hypotheses_status.values() 
                         if h in ['✅', '🟢'])
        
        message = f"""{emoji} *Rxx Engine Alert - {datetime.now().strftime('%H:%M')}*
        
📊 *IDD Score*: {idd_score}/100 ({level})
✅ *Hypothèses*: {valid_count}/8 validées
📈 *Battery Metals*: {hypotheses_status.get('battery_bull', '?')}/6 en bull

🔍 *Détail*:
"""
        # Ajouter chaque hypothèse
        for hyp_id, status in hypotheses_status.items():
            if hyp_id != 'battery_bull':
                message += f"  {status} {hyp_id}\n"
        
        # Envoyer via Telegram
        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        response = requests.post(url, json={
            'chat_id': self.chat_id,
            'text': message,
            'parse_mode': 'Markdown',
            'disable_notification': not notify
        })
        
        return response.status_code == 200

# Utilisation dans Rxx_Engine_V17.0.py
# Ajouter en début de main():
# alerter = TelegramAlerter(bot_token="TON_TOKEN", chat_id="TON_CHAT_ID")
# À la fin, après calcul IDD:
# alerter.send_idd_alert(idd['score'], {h: d['resultat'] for h, d in hypotheses.items()})
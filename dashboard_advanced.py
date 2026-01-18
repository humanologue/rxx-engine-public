# dashboard_final.py - VERSION CORRIGÉE (fichier unique)
import json
import sqlite3
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

class RxxDashboardFinal:
    """Dashboard final - TOUT DANS UN SEUL FICHIER HTML"""
    
    def __init__(self):
        print("🚀 Initialisation du Dashboard Rxx Engine (version unique)...")
        self.load_data()
        self.connect_db()
        
    def load_data(self):
        """Charge toutes les données avec gestion robuste des clés manquantes"""
        try:
            # 1. Charger les fichiers JSON
            with open('validation_report.json', 'r', encoding='utf-8') as f:
                self.vdata = json.load(f)
            with open('hypotheses_check.json', 'r', encoding='utf-8') as f:
                self.hdata = json.load(f)
            
            # 2. Charger le CSV (avec gestion d'erreur)
            try:
                self.csv_data = pd.read_csv('monitoring_enhanced.csv', sep=';')
            except Exception as csv_error:
                print(f"⚠️  CSV non chargé: {csv_error}")
                self.csv_data = pd.DataFrame()
            
            # 3. EXTRAIRE LES DONNÉES DE MANIÈRE ROBUSTE (avec valeurs par défaut)
            # IDD Score et Décision
            self.idd_score = self.vdata.get('idd', {}).get('score', 0.0)  # Valeur par défaut: 0
            self.idd_decision = self.vdata.get('idd', {}).get('decision', '📊 NON CALCULÉ')
            
            # Battery Metals
            battery_data = self.vdata.get('battery_metals', {})
            self.battery_bull = battery_data.get('bull_count', 0)
            
            # Statistiques - Teste plusieurs noms de clé possibles
            stats = self.vdata.get('statistiques', {})
            # Essayer différentes orthographes de la clé
            self.hypotheses_ok = stats.get('hypothèses_ok') or stats.get('hypotheses_ok') or 0
            
            # Valeurs critiques (pour les alertes)
            self.critical_values = self.vdata.get('valeurs_critiques', {})
            
            print(f"✅ Données chargées: IDD={self.idd_score}, Battery={self.battery_bull}/6, Hypothèses OK={self.hypotheses_ok}")
            
        except FileNotFoundError as e:
            print(f"❌ Fichier manquant: {e.filename}")
            print("   Exécutez d'abord votre moteur Rxx avec: python Rxx_Engine_V17.0.py")
            raise
        except json.JSONDecodeError as e:
            print(f"❌ Fichier JSON corrompu: {e}")
            raise
        except Exception as e:
            print(f"❌ Erreur inattendue lors du chargement: {e}")
            raise
    
    def connect_db(self):
        """Connexion à la base de données historique"""
        try:
            self.conn = sqlite3.connect("rxx_history.db")
            self.history = pd.read_sql_query("""
                SELECT execution_id, start_time, idd_score, battery_bull, hypotheses_ok
                FROM executions ORDER BY start_time DESC LIMIT 50
            """, self.conn)
            if not self.history.empty:
                self.history['start_time'] = pd.to_datetime(self.history['start_time'])
                print(f"📅 Historique chargé: {len(self.history)} exécutions")
        except Exception as e:
            print(f"⚠️  Base de données: {e}")
            self.conn = None
    
    def generate_all_charts_html(self):
        """Génère le code HTML pour tous les graphiques et les renvoie dans un dictionnaire"""
        charts_html = {}
        
        # 1. Graphique IDD
        if self.conn and not self.history.empty:
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=self.history['start_time'], y=self.history['idd_score'],
                mode='lines+markers', name='IDD Score',
                line=dict(color='#FF6B6B', width=4)))
            fig.update_layout(title='📈 ÉVOLUTION IDD', height=400)
            charts_html['idd'] = fig.to_html(full_html=False, include_plotlyjs=False)
        
        # 2. Graphique Hypothèses (Camembert)
        results = [h['resultat'] for h in self.hdata.values()]
        counts = {'✅ Validé': results.count('✅') + results.count('🟢'),
                 '⚠️ Mitigé': results.count('⚪') + results.count('🟡') + results.count('⚠️'),
                 '❌ Invalidé': results.count('❌')}
        fig = go.Figure(data=[go.Pie(labels=list(counts.keys()), values=list(counts.values()), hole=0.5)])
        fig.update_layout(title='📊 RÉPARTITION DES HYPOTHÈSES', height=400)
        charts_html['hypotheses'] = fig.to_html(full_html=False, include_plotlyjs=False)
        
        # 3. Graphique Battery Metals
        if self.conn and not self.history.empty:
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=self.history['start_time'], y=self.history['battery_bull'],
                mode='lines+markers', name='Battery Metals Bull',
                line=dict(color='#3498db', width=4)))
            fig.update_layout(title='🔋 BATTERY METALS - Historique Bull', height=400, yaxis_range=[0, 6])
            charts_html['battery'] = fig.to_html(full_html=False, include_plotlyjs=False)
        
        # 4. Tableau des Alertes (simplifié pour l'exemple)
        fig = go.Figure()
        fig.add_annotation(text="✅ <b>FONCTIONNALITÉ ALERTES</b><br>À intégrer séparément", 
                          xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False, font=dict(size=20))
        fig.update_layout(title='🚨 ALERTES ACTIVES', height=300)
        charts_html['alerts'] = fig.to_html(full_html=False, include_plotlyjs=False)
        
        print("✅ Tous les graphiques générés en HTML")
        return charts_html
    
    def create_single_html_dashboard(self):
        """Crée un dashboard COMPLET dans un seul fichier HTML"""
        current_time = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        total_runs = len(self.history) if hasattr(self, 'history') and not self.history.empty else 0
        avg_idd = self.history['idd_score'].mean() if total_runs > 0 else 0
        idd_color = '#27ae60' if self.idd_score >= 75 else '#f39c12' if self.idd_score >= 50 else '#e74c3c'
        
        # Générer le HTML de tous les graphiques
        charts = self.generate_all_charts_html()
        
        # Construction du HTML principal
        html_template = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Rxx Engine V17.0 - Dashboard Unique</title>
    <script src="https://cdn.plot.ly/plotly-2.18.0.min.js"></script>
    <style>
        body {{ font-family: 'Segoe UI', Arial, sans-serif; margin: 20px; background: #f5f7fa; }}
        .container {{ max-width: 1400px; margin: 0 auto; background: white; padding: 30px; border-radius: 15px; box-shadow: 0 5px 15px rgba(0,0,0,0.1); }}
        .header {{ text-align: center; padding-bottom: 20px; border-bottom: 2px solid #2c3e50; margin-bottom: 30px; }}
        .stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 30px 0; }}
        .stat-card {{ background: #f8f9fa; padding: 20px; border-radius: 10px; text-align: center; border: 1px solid #dee2e6; }}
        .stat-value {{ font-size: 2.5em; font-weight: bold; margin: 10px 0; color: #2c3e50; }}
        .dashboard-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(600px, 1fr)); gap: 25px; margin: 30px 0; }}
        .chart-container {{ background: white; padding: 15px; border-radius: 10px; border: 1px solid #e9ecef; }}
        .footer {{ text-align: center; margin-top: 30px; padding-top: 20px; border-top: 1px solid #eee; color: #7f8c8d; font-size: 0.9em; }}
        @media (max-width: 768px) {{ .dashboard-grid {{ grid-template-columns: 1fr; }} }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1 style="color: #2c3e50; margin-bottom: 5px;">🚀 Rxx Engine V17.0 Dashboard</h1>
            <p style="color: #7f8c8d;">📊 Surveillance géopolitique et économique | Généré le: {current_time}</p>
        </div>
        
        <div class="stats">
            <div class="stat-card">
                <div style="color: #7f8c8d; font-weight: 600;">🎯 IDD Score</div>
                <div class="stat-value">{self.idd_score}</div>
                <div style="color: {idd_color}; font-weight: bold;">{self.idd_decision}</div>
            </div>
            <div class="stat-card">
                <div style="color: #7f8c8d; font-weight: 600;">✅ Hypothèses</div>
                <div class="stat-value">{self.hypotheses_ok}/8</div>
                <div>{int(self.hypotheses_ok/8*100)}% validées</div>
            </div>
            <div class="stat-card">
                <div style="color: #7f8c8d; font-weight: 600;">🔋 Battery Metals</div>
                <div class="stat-value">{self.battery_bull}/6</div>
                <div>{self.vdata['battery_metals']['supercycle']}</div>
            </div>
            <div class="stat-card">
                <div style="color: #7f8c8d; font-weight: 600;">📅 Exécutions</div>
                <div class="stat-value">{total_runs}</div>
                <div>Moyenne: {avg_idd:.1f}</div>
            </div>
        </div>
        
        <div class="dashboard-grid">
            <div class="chart-container">
                <h3>📈 Évolution de l'IDD</h3>
                {charts.get('idd', '<p>Données non disponibles</p>')}
            </div>
            <div class="chart-container">
                <h3>📊 Répartition des Hypothèses</h3>
                {charts.get('hypotheses', '<p>Données non disponibles</p>')}
            </div>
            <div class="chart-container">
                <h3>🔋 Battery Metals - Historique</h3>
                {charts.get('battery', '<p>Données non disponibles</p>')}
            </div>
            <div class="chart-container">
                <h3>🚨 Alertes Actives</h3>
                {charts.get('alerts', '<p>Données non disponibles</p>')}
            </div>
        </div>
        
        <div class="footer">
            <p>🔄 Rxx Engine V17.0 | Dashboard généré automatiquement</p>
            <p>Dernière mise à jour: {current_time} | Actualisation automatique désactivée</p>
        </div>
    </div>
    
    <script>
        // Script minimal pour une éventuelle actualisation manuelle
        console.log("Dashboard Rxx Engine chargé avec succès");
    </script>
</body>
</html>
"""
        # Écriture du fichier
        output_file = 'RXX_DASHBOARD_FINAL_SINGLE.html'
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_template)
        
        print(f"✅ Dashboard unique généré : {output_file}")
        return output_file
    
    def run(self):
        """Exécute la génération du dashboard"""
        print("\n" + "="*60)
        print("🚀 GÉNÉRATION DU DASHBOARD (FICHIER UNIQUE)")
        print("="*60)
        try:
            output_file = self.create_single_html_dashboard()
            print("\n" + "="*60)
            print("✅ DASHBOARD GÉNÉRÉ AVEC SUCCÈS !")
            print("="*60)
            print(f"\n📁 FICHIER CRÉÉ : {output_file}")
            print("\n🌐 OUVREZ-LE DANS VOTRE NAVIGATEUR :")
            print(f"   {output_file}")
            
            # Ouvrir automatiquement dans le navigateur par défaut
            import webbrowser, os
            webbrowser.open('file://' + os.path.realpath(output_file))
            
        except Exception as e:
            print(f"\n❌ ERREUR: {e}")
            import traceback
            traceback.print_exc()

# Point d'entrée
if __name__ == "__main__":
    import os
    required = ['validation_report.json', 'hypotheses_check.json', 'monitoring_enhanced.csv']
    for file in required:
        if not os.path.exists(file):
            print(f"❌ Fichier manquant: {file}")
            print("   Exécutez d'abord votre moteur Rxx pour générer les données.")
            exit(1)
    
    dashboard = RxxDashboardFinal()
    dashboard.run()
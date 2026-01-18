# analyse_history.py
#!/usr/bin/env python3
"""
Script d'analyse des données historiques
"""

from db_integration import RxxDatabase
import pandas as pd
import matplotlib.pyplot as plt

def main():
    db = RxxDatabase()
    
    print("📊 ANALYSE DES DONNÉES HISTORIQUES Rxx")
    print("="*60)
    
    # 1. Dernières exécutions
    last_execs = db.get_last_n_executions(10)
    print(f"\n📈 Dernières 10 exécutions:")
    print(last_execs[['start_time', 'idd_score', 'success_rate', 'hypotheses_ok']].to_string())
    
    # 2. Alertes récentes
    alerts = db.get_alerts_history(7)
    if not alerts.empty:
        print(f"\n🚨 Alertes (7 derniers jours): {len(alerts)}")
        print(alerts[['timestamp', 'node_id', 'valeur_text', 'domaine']].to_string())
    
    # 3. Tendances des nœuds critiques
    print(f"\n📉 Tendances des nœuds critiques (7 jours):")
    critical_nodes = ['R11', 'R24', 'R00', 'R81', 'R91']
    for node in critical_nodes:
        trends = db.calculate_trends(node, 7)
        if "error" not in trends:
            print(f"   {node}: {trends['current']} → {trends['trend']} (volatilité: {trends['volatility']:.1f}%)")
    
    # 4. Générer un dashboard
    dashboard = db.generate_dashboard_data(30)
    print(f"\n📋 Dashboard résumé:")
    print(f"   Exécutions analysées: {len(dashboard['summary'].get('last_executions', []))}")
    print(f"   IDD moyen: {dashboard['summary'].get('avg_idd', 0):.1f}")
    print(f"   Taux de succès: {dashboard['summary'].get('success_rate', 0):.1f}%")
    
    # 5. Export pour visualisation
    export_file = db.export_to_json("dashboard_data.json")
    print(f"\n💾 Données exportées: {export_file}")
    
    print("\n✅ Analyse terminée!")

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
# test_db.py - Test autonome du module db_integration

import sys
from pathlib import Path

# Ajouter le dossier courant au path pour importer le module
sys.path.insert(0, str(Path.cwd()))

def test_simple():
    """Test simple du module db_integration"""
    print("🧪 TEST DU MODULE DB_INTEGRATION")
    print("="*60)
    
    try:
        from db_integration import RxxDatabase
        
        # 1. Créer une base de test
        print("\n1. Création de la base de données...")
        db = RxxDatabase("test_rxx.db", retention_days=7)
        print(f"   ✅ Base créée : {db.db_path}")
        
        # 2. Tester avec des données simulées
        print("\n2. Test avec données simulées...")
        
        # Données de test
        test_data = {
            "R11": {
                "valeur_live": "19.8",
                "domaine": "ENERGIE",
                "priorite": "🔴",
                "statut_contextuel": "🚨 CRITIQUE",
                "alerte_seuil": "🚨",
                "hypothese_liee": "H1_P4",
                "statut_exec": "OK",
                "seuil": "<20",
                "timestamp": "2026-01-17 05:00 CET"
            },
            "R24": {
                "valeur_live": "37.63",
                "domaine": "ENERGIE", 
                "priorite": "🔴",
                "statut_contextuel": "✅ BAS",
                "alerte_seuil": "✅",
                "hypothese_liee": "H1_P4",
                "statut_exec": "OK",
                "seuil": "<40",
                "timestamp": "2026-01-17 05:00 CET"
            }
        }
        
        test_hypotheses = {
            "H1_P4": {
                "resultat": "✅",
                "details": "R11=19.8% (15-25%) | R24=€37.63 (25-50€)",
                "condition": "15% ≤ R11 ≤ 25% ET 25 ≤ R24 ≤ 50"
            }
        }
        
        test_battery = {
            "details": {
                "R65": {
                    "metal": "Silver",
                    "valeur": 51.23,
                    "seuil": 30,
                    "unite": "$/oz",
                    "statut": "🟢 BULL",
                    "bull": True
                }
            },
            "bull_count": 3,
            "total": 6,
            "supercycle": "⚠️ MODÉRÉ",
            "recommandation": "🟡 Surveillance accrue"
        }
        
        test_idd = {
            "score": 68.8,
            "decision": "🟡 SURVEILLANCE",
            "description": "Conditions mitigées, vigilance requise",
            "hypotheses_evaluees": 8,
            "ok": 5
        }
        
        # Stocker les données
        exec_id = db.store_execution(
            donnees_enhanced=test_data,
            hypotheses=test_hypotheses,
            battery_matrix=test_battery,
            idd=test_idd,
            metadata={"total_nodes": 2, "scripts_executed": 2, "numerical_values": 2}
        )
        
        print(f"   ✅ Exécution stockée : {exec_id}")
        
        # 3. Tester les requêtes
        print("\n3. Test des requêtes...")
        
        # Dernières exécutions
        last_execs = db.get_last_n_executions(5)
        print(f"   📋 Dernières exécutions : {len(last_execs)} trouvée(s)")
        
        # Historique R11
        history = db.get_node_history("R11", 7)
        print(f"   📊 Historique R11 : {len(history)} point(s) de données")
        
        # Alertes
        alerts = db.get_alerts_history(1)
        print(f"   🚨 Alertes : {len(alerts)} alerte(s)")
        
        # 4. Exporter en JSON
        print("\n4. Export des données...")
        export_file = db.export_to_json("test_export.json")
        print(f"   💾 Fichier exporté : {export_file}")
        
        # 5. Vérifier le fichier
        import json
        with open(export_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            print(f"   📈 IDD moyen dans l'export : {data['summary'].get('avg_idd', 0):.1f}")
        
        print("\n" + "="*60)
        print("✅ TEST RÉUSSI ! Le module fonctionne correctement.")
        
        # Nettoyage optionnel
        cleanup = input("\n🧹 Supprimer les fichiers de test ? (o/N): ")
        if cleanup.lower() == 'o':
            Path("test_rxx.db").unlink(missing_ok=True)
            Path("test_export.json").unlink(missing_ok=True)
            print("   Fichiers supprimés.")
        
    except Exception as e:
        print(f"\n❌ ERREUR : {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

def test_with_real_data():
    """Test avec les données réelles générées par r_dynamo.py"""
    print("\n" + "="*60)
    print("🧪 TEST AVEC DONNÉES RÉELLES")
    print("="*60)
    
    # Vérifier que r_dynamo.py a été exécuté
    required_files = ["monitoring_enhanced.csv", "validation_report.json", "hypotheses_check.json"]
    
    for file in required_files:
        if not Path(file).exists():
            print(f"❌ Fichier manquant : {file}")
            print("💡 Exécutez d'abord: python r_dynamo.py")
            return False
    
    try:
        from db_integration import integrate_with_engine_v17
        
        print("\n1. Intégration des données réelles...")
        db, exec_id = integrate_with_engine_v17()
        
        if not db:
            print("❌ Échec de l'intégration")
            return False
        
        print(f"✅ Données intégrées (ID: {exec_id})")
        
        # 2. Analyse des données
        print("\n2. Analyse des données historiques...")
        
        # Statistiques
        last_execs = db.get_last_n_executions(5)
        print(f"   📅 Exécutions stockées : {len(last_execs)}")
        
        if not last_execs.empty:
            avg_idd = last_execs['idd_score'].mean()
            print(f"   📈 IDD moyen : {avg_idd:.1f}/100")
            
            success_rate = last_execs['success_rate'].mean()
            print(f"   ✅ Taux de succès : {success_rate:.1f}%")
        
        # Alertes récentes
        alerts = db.get_alerts_history(1)
        print(f"   🚨 Alertes 24h : {len(alerts)}")
        
        if not alerts.empty:
            print("   📋 Dernières alertes:")
            for _, alert in alerts.head(3).iterrows():
                print(f"     • {alert['node_id']} = {alert['valeur_text']} ({alert['domaine']})")
        
        # 3. Export pour visualisation
        print("\n3. Génération du dashboard...")
        export_file = db.export_to_json("rxx_dashboard_data.json")
        print(f"   💾 Dashboard exporté : {export_file}")
        
        # 4. Interface simple en ligne de commande
        print("\n4. Interface de requêtes:")
        print("   [1] Historique d'un nœud")
        print("   [2] Alertes récentes")
        print("   [3] Tendances")
        print("   [4] Quitter")
        
        while True:
            choice = input("\n   Votre choix (1-4): ").strip()
            
            if choice == "1":
                node_id = input("   Nœud (ex: R11, R24): ").strip().upper()
                history = db.get_node_history(node_id, 7)
                if history.empty:
                    print(f"   ❌ Aucune donnée pour {node_id}")
                else:
                    print(f"\n   📊 Historique {node_id} (7 jours):")
                    print(history[['timestamp', 'valeur', 'statut_contextuel']].to_string(index=False))
            
            elif choice == "2":
                days = input("   Nombre de jours (défaut: 7): ").strip() or "7"
                alerts = db.get_alerts_history(int(days))
                if alerts.empty:
                    print(f"   ✅ Aucune alerte sur {days} jours")
                else:
                    print(f"\n   🚨 Alertes ({days} jours): {len(alerts)}")
                    print(alerts[['timestamp', 'node_id', 'valeur_text', 'domaine']].to_string(index=False))
            
            elif choice == "3":
                node_id = input("   Nœud pour analyse de tendance (ex: R11): ").strip().upper()
                trends = db.calculate_trends(node_id, 7)
                if "error" in trends:
                    print(f"   ❌ {trends['error']}")
                else:
                    print(f"\n   📈 Analyse {node_id}:")
                    print(f"      Actuel: {trends['current']}")
                    print(f"      Tendance: {trends['trend']}")
                    print(f"      Moyenne: {trends['mean']:.2f}")
                    print(f"      Volatilité: {trends['volatility']:.1f}%")
                    print(f"      Points: {trends['data_points']}")
            
            elif choice == "4":
                print("   👋 Au revoir!")
                break
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERREUR : {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🔧 MENU DE TEST - DB_INTEGRATION")
    print("="*60)
    print("1. Test simple avec données simulées")
    print("2. Test avec données réelles (après r_dynamo.py)")
    print("3. Quitter")
    
    choice = input("\nVotre choix (1-3): ").strip()
    
    if choice == "1":
        test_simple()
    elif choice == "2":
        # Vérifier que r_dynamo.py a été exécuté
        if not Path("monitoring_enhanced.csv").exists():
            print("\n⚠️  Exécutez d'abord r_dynamo.py pour générer les données")
            print("   Commande: python r_dynamo.py")
        else:
            test_with_real_data()
    elif choice == "3":
        print("👋 Au revoir!")
    else:
        print("❌ Choix invalide")
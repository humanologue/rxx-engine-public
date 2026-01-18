# analyse_db_v2.py
import sqlite3
import pandas as pd
import json
from datetime import datetime, timedelta
from pathlib import Path
import plotly.graph_objects as go
from plotly.subplots import make_subplots

class RxxDatabaseAnalyzerV2:
    """Analyseur adapté à la structure réelle de rxx_history.db"""
    
    def __init__(self, db_path="rxx_history.db", ontologie_path="ontologie.json"):
        self.db_path = Path(db_path)
        self.ontologie_path = Path(ontologie_path)
        self.conn = None
        self.ontologie = None
        
        print("=" * 70)
        print("📊 ANALYSEUR Rxx Engine V2")
        print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M CET')}")
        print("=" * 70)
        
        if not self.db_path.exists():
            print(f"❌ Base de données introuvable: {self.db_path}")
            return
        
        self.load_ontologie()
        self.connect_db()
        self.analyze_complete()
    
    def load_ontologie(self):
        """Charge l'ontologie JSON"""
        if self.ontologie_path.exists():
            try:
                with open(self.ontologie_path, 'r', encoding='utf-8') as f:
                    self.ontologie = json.load(f)
                print(f"✅ Ontologie chargée: {len(self.ontologie.get('noeuds', {}))} nœuds")
            except Exception as e:
                print(f"❌ Erreur chargement ontologie: {e}")
                self.ontologie = None
        else:
            print("⚠️  Ontologie non trouvée")
            self.ontologie = None
    
    def connect_db(self):
        """Connexion à la base SQLite"""
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row  # Pour accès par nom de colonne
            print(f"✅ Base connectée: {self.db_path}")
            print(f"📊 Taille: {self.db_path.stat().st_size / 1024 / 1024:.2f} MB")
        except Exception as e:
            print(f"❌ Erreur connexion DB: {e}")
    
    def get_database_stats(self):
        """Statistiques générales de la base"""
        cursor = self.conn.cursor()
        
        print("\n" + "=" * 70)
        print("📈 STATISTIQUES GÉNÉRALES")
        print("=" * 70)
        
        # Nombre d'exécutions
        cursor.execute("SELECT COUNT(*) FROM executions")
        total_exec = cursor.fetchone()[0]
        
        # Période couverte
        cursor.execute("SELECT MIN(start_time), MAX(start_time) FROM executions")
        min_date, max_date = cursor.fetchone()
        
        # Nœuds uniques
        cursor.execute("SELECT COUNT(DISTINCT node_id) FROM rxx_data")
        unique_nodes = cursor.fetchone()[0]
        
        # Total mesures
        cursor.execute("SELECT COUNT(*) FROM rxx_data")
        total_measures = cursor.fetchone()[0]
        
        print(f"📊 Données stockées:")
        print(f"  • Exécutions: {total_exec}")
        print(f"  • Période: {min_date} → {max_date}")
        print(f"  • Nœuds uniques: {unique_nodes}")
        print(f"  • Mesures totales: {total_measures:,}")
        
        # IDD moyenne
        cursor.execute("SELECT AVG(idd_score) FROM executions")
        avg_idd = cursor.fetchone()[0]
        print(f"  • IDD moyen: {avg_idd:.1f}/100")
        
        return {
            'total_executions': total_exec,
            'period': (min_date, max_date),
            'unique_nodes': unique_nodes,
            'total_measures': total_measures,
            'avg_idd': avg_idd
        }
    
    def analyze_recent_executions(self, limit=10):
        """Analyse des dernières exécutions - VERSION CORRIGÉE"""
        print("\n" + "=" * 70)
        print(f"🔄 {limit} DERNIÈRES EXÉCUTIONS")
        print("=" * 70)
        
        # REQUÊTE CORRIGÉE : sans success_count et error_count qui n'existent pas
        query = """
        SELECT 
            execution_id,
            start_time,
            total_nodes,
            scripts_executed,
            numerical_values,
            hypotheses_ok,
            hypotheses_total,
            battery_bull,
            battery_total,
            idd_score,
            idd_decision,
            duration_seconds,
            status
        FROM executions 
        ORDER BY start_time DESC
        LIMIT ?
        """
        
        df = pd.read_sql_query(query, self.conn, params=(limit,))
        
        if len(df) > 0:
            # Afficher les colonnes disponibles
            print("Colonnes disponibles:", list(df.columns))
            
            # Afficher un aperçu
            display_cols = ['execution_id', 'start_time', 'total_nodes', 'idd_score', 'idd_decision', 'status']
            display_cols = [col for col in display_cols if col in df.columns]
            
            print(df[display_cols].to_string())
            
            # Calculer taux de succès basé sur status
            if 'status' in df.columns:
                success_rate = (df['status'] == 'COMPLETED').mean() * 100 if len(df) > 0 else 0
                print(f"\n📊 Taux de succès (status='COMPLETED'): {success_rate:.1f}%")
            
            # Tendances IDD
            print(f"\n📈 TENDANCES IDD:")
            if len(df) > 1:
                latest_idd = df['idd_score'].iloc[0]
                prev_idd = df['idd_score'].iloc[1] if len(df) > 1 else latest_idd
                change = latest_idd - prev_idd
                trend = "↗️ Hausse" if change > 0 else "↘️ Baisse" if change < 0 else "➡️ Stable"
                print(f"  Actuel: {latest_idd:.1f} ({trend} {change:+.1f})")
                
                # Moyenne
                avg_idd = df['idd_score'].mean()
                print(f"  Moyenne {len(df)} exécutions: {avg_idd:.1f}")
                
                # Décision actuelle
                if 'idd_decision' in df.columns:
                    print(f"  Décision: {df['idd_decision'].iloc[0]}")
            
            # Statistiques d'exécution
            print(f"\n⚡ PERFORMANCE:")
            if 'duration_seconds' in df.columns:
                avg_duration = df['duration_seconds'].mean()
                print(f"  Durée moyenne: {avg_duration:.1f}s")
            
            if 'numerical_values' in df.columns and 'total_nodes' in df.columns:
                success_rate_nodes = (df['numerical_values'] / df['total_nodes']).mean() * 100
                print(f"  Taux extraction données: {success_rate_nodes:.1f}%")
            
            return df
        else:
            print("❌ Aucune donnée d'exécution")
            return None
            
    def analyze_executions_stats(self):
        """Statistiques avancées sur les exécutions - NOUVELLE FONCTION"""
        print("\n" + "=" * 70)
        print("📊 STATISTIQUES D'EXÉCUTION")
        print("=" * 70)
        
        query = """
        SELECT 
            COUNT(*) as total_executions,
            AVG(total_nodes) as avg_nodes,
            AVG(scripts_executed) as avg_scripts,
            AVG(numerical_values) as avg_numerical,
            AVG(idd_score) as avg_idd,
            AVG(duration_seconds) as avg_duration,
            SUM(CASE WHEN status = 'COMPLETED' THEN 1 ELSE 0 END) as completed_count,
            MIN(start_time) as first_execution,
            MAX(start_time) as last_execution
        FROM executions
        """
        
        cursor = self.conn.cursor()
        cursor.execute(query)
        stats = cursor.fetchone()
        
        if stats and stats['total_executions'] > 0:
            print(f"📈 SUR L'ENSEMBLE DES EXÉCUTIONS:")
            print(f"  • Total: {stats['total_executions']} exécutions")
            print(f"  • Période: {stats['first_execution']} → {stats['last_execution']}")
            print(f"  • IDD moyen: {stats['avg_idd']:.1f}/100")
            print(f"  • Durée moyenne: {stats['avg_duration']:.1f}s")
            print(f"  • Nœuds moyens/exécution: {stats['avg_nodes']:.0f}")
            print(f"  • Scripts moyens/exécution: {stats['avg_scripts']:.0f}")
            print(f"  • Valeurs numériques moyennes: {stats['avg_numerical']:.0f}")
            print(f"  • Exécutions complétées: {stats['completed_count']} ({stats['completed_count']/stats['total_executions']*100:.1f}%)")
            
            # Distribution des décisions IDD
            query_dist = """
            SELECT idd_decision, COUNT(*) as count
            FROM executions
            GROUP BY idd_decision
            ORDER BY count DESC
            """
            
            cursor.execute(query_dist)
            decisions = cursor.fetchall()
            
            if decisions:
                print(f"\n🎯 DISTRIBUTION DES DÉCISIONS:")
                for decision in decisions:
                    percentage = (decision['count'] / stats['total_executions']) * 100
                    print(f"  {decision['idd_decision']}: {decision['count']} fois ({percentage:.1f}%)")
            
            return stats
        else:
            print("❌ Aucune statistique disponible")
            return None
    
    def analyze_nodes_activity(self):
        """Analyse de l'activité des nœuds"""
        print("\n" + "=" * 70)
        print("🎯 ACTIVITÉ DES NŒUDS")
        print("=" * 70)
        
        query = """
        SELECT 
            node_id,
            COUNT(*) as mesures,
            AVG(valeur) as moyenne,
            MIN(valeur) as minimum,
            MAX(valeur) as maximum,
            MIN(timestamp) as first_seen,
            MAX(timestamp) as last_seen
        FROM rxx_data
        WHERE valeur IS NOT NULL
        GROUP BY node_id
        HAVING COUNT(*) > 5
        ORDER BY mesures DESC
        LIMIT 20
        """
        
        df = pd.read_sql_query(query, self.conn)
        
        if len(df) > 0:
            print(f"Top {len(df)} nœuds les plus actifs:")
            print(df[['node_id', 'mesures', 'moyenne', 'minimum', 'maximum']].to_string())
            
            # Corrélation avec ontologie
            if self.ontologie:
                print(f"\n🔗 CONTEXTE ONTOLOGIE:")
                nodes_info = self.ontologie.get('noeuds', {})
                for _, row in df.head(10).iterrows():
                    node_id = row['node_id']
                    if node_id in nodes_info:
                        info = nodes_info[node_id]
                        print(f"  {node_id}: {info.get('domaine', 'N/A')} - {info.get('donnee', 'N/A')}")
            
            return df
        else:
            print("❌ Aucune donnée de nœud")
            return None
    
    def analyze_gdelt_data(self):
        """Analyse spécifique des données GDELT"""
        print("\n" + "=" * 70)
        print("🌍 DONNÉES GDELT")
        print("=" * 70)
        
        # Nœuds GDELT
        gdelt_nodes = ['R32', 'R32_17', 'R32_18', 'R32_20', 'R33', 'R33_acled']
        
        results = []
        for node in gdelt_nodes:
            query = """
            SELECT 
                COUNT(*) as mesures,
                AVG(valeur) as moyenne,
                MIN(valeur) as minimum,
                MAX(valeur) as maximum,
                MAX(timestamp) as dernier
            FROM rxx_data
            WHERE node_id = ? AND valeur IS NOT NULL
            """
            
            cursor = self.conn.cursor()
            cursor.execute(query, (node,))
            row = cursor.fetchone()
            
            if row and row['mesures'] > 0:
                results.append({
                    'node_id': node,
                    'mesures': row['mesures'],
                    'moyenne': row['moyenne'],
                    'min': row['minimum'],
                    'max': row['maximum'],
                    'dernier': row['dernier']
                })
        
        if results:
            print("📊 Statistiques GDELT:")
            for res in results:
                print(f"  {res['node_id']}: {res['mesures']} mesures, moy={res['moyenne']:.1f}, dernier={res['dernier']}")
            
            # Analyse de dernière exécution
            print(f"\n📅 DERNIÈRE EXÉCUTION GDELT:")
            query = """
            SELECT node_id, valeur, timestamp
            FROM rxx_data
            WHERE node_id IN ('R32', 'R32_17', 'R32_18', 'R32_20')
            AND timestamp = (SELECT MAX(timestamp) FROM rxx_data WHERE node_id LIKE 'R32%')
            ORDER BY node_id
            """
            
            df_last = pd.read_sql_query(query, self.conn)
            if len(df_last) > 0:
                print(df_last.to_string())
                
                # Vérifier cohérence
                print(f"\n🔍 VÉRIFICATION COHÉRENCE:")
                for _, row in df_last.iterrows():
                    node_id = row['node_id']
                    valeur = row['valeur']
                    
                    # Logique de vérification simple
                    if node_id == 'R32_20' and valeur > 500:
                        print(f"  ⚠️  {node_id}={valeur}: Manifestations très élevées")
                    elif node_id == 'R32_17' and valeur > 50:
                        print(f"  ⚠️  {node_id}={valeur}: Répression élevée")
                    elif node_id == 'R32_18' and valeur < 1000:
                        print(f"  ✅ {node_id}={valeur}: Manifestations normales")
            
            return results
        else:
            print("❌ Aucune donnée GDELT trouvée")
            return None
    
    def analyze_temporal_trend(self, node_id="R32", days_back=7):
        """Analyse des tendances temporelles pour un nœud"""
        print("\n" + "=" * 70)
        print(f"📈 TENDANCE {node_id} (7 derniers jours)")
        print("=" * 70)
        
        query = """
        SELECT 
            timestamp,
            valeur
        FROM rxx_data
        WHERE node_id = ?
        AND valeur IS NOT NULL
        AND timestamp >= datetime('now', ?)
        ORDER BY timestamp
        """
        
        cursor = self.conn.cursor()
        cursor.execute(query, (node_id, f'-{days_back} days'))
        rows = cursor.fetchall()
        
        if rows:
            timestamps = [row['timestamp'] for row in rows]
            values = [row['valeur'] for row in rows]
            
            print(f"📊 {len(rows)} mesures pour {node_id}")
            
            # Statistiques
            if len(values) > 0:
                avg_val = sum(values) / len(values)
                min_val = min(values)
                max_val = max(values)
                last_val = values[-1]
                
                print(f"  Moyenne: {avg_val:.1f}")
                print(f"  Min/Max: {min_val:.1f} / {max_val:.1f}")
                print(f"  Dernière: {last_val:.1f}")
                
                if len(values) > 1:
                    # Variation %
                    first_val = values[0]
                    change_pct = ((last_val - first_val) / first_val * 100) if first_val != 0 else 0
                    print(f"  Variation {days_back}j: {change_pct:+.1f}%")
                    
                    # Détection d'anomalie
                    std_dev = (sum((v - avg_val) ** 2 for v in values) / len(values)) ** 0.5
                    if std_dev > 0:
                        z_score = abs((last_val - avg_val) / std_dev)
                        if z_score > 2:
                            print(f"  ⚠️  ANOMALIE: z-score = {z_score:.2f}")
            
            # Afficher les valeurs récentes
            print(f"\n📅 VALEURS RÉCENTES:")
            for i in range(min(5, len(rows))):
                row = rows[-(i+1)]
                print(f"  {row['timestamp']}: {row['valeur']}")
            
            return rows
        else:
            print(f"❌ Aucune donnée pour {node_id} sur {days_back} jours")
            return None
    
    def analyze_hypotheses_performance(self):
        """Analyse de la performance des hypothèses DYNAMO"""
        print("\n" + "=" * 70)
        print("🧪 PERFORMANCE DES HYPOTHÈSES")
        print("=" * 70)
        
        query = """
        SELECT 
            hypothesis_id,
            resultat,
            COUNT(*) as occurrences,
            ROUND(AVG(CASE WHEN resultat = '✅' THEN 1 ELSE 0 END) * 100, 1) as success_rate
        FROM hypotheses
        GROUP BY hypothesis_id, resultat
        ORDER BY hypothesis_id, occurrences DESC
        """
        
        df = pd.read_sql_query(query, self.conn)
        
        if len(df) > 0:
            print("📊 Fréquence des résultats:")
            for hyp_id in df['hypothesis_id'].unique():
                hyp_data = df[df['hypothesis_id'] == hyp_id]
                print(f"\n  {hyp_id}:")
                for _, row in hyp_data.iterrows():
                    print(f"    {row['resultat']}: {row['occurrences']} fois ({row['success_rate']}%)")
            
            # Taux de succès global
            total_ok = len(df[df['resultat'] == '✅'])
            total_all = len(df)
            if total_all > 0:
                global_rate = (total_ok / total_all) * 100
                print(f"\n📈 Taux de succès global: {global_rate:.1f}%")
            
            return df
        else:
            print("❌ Aucune donnée d'hypothèse")
            return None
    
    def analyze_battery_metals(self):
        """Analyse de la matrice Battery Metals"""
        print("\n" + "=" * 70)
        print("🔋 MATRICE BATTERY METALS")
        print("=" * 70)
        
        query = """
        SELECT 
            node_id,
            metal,
            AVG(valeur) as avg_value,
            COUNT(*) as mesures,
            SUM(CASE WHEN bull = 1 THEN 1 ELSE 0 END) as bull_count
        FROM battery_metals
        GROUP BY node_id, metal
        ORDER BY node_id
        """
        
        df = pd.read_sql_query(query, self.conn)
        
        if len(df) > 0:
            print("📊 Statistiques Battery Metals:")
            print(df.to_string())
            
            # Analyse globale
            total_bull = df['bull_count'].sum()
            total_measures = df['mesures'].sum()
            if total_measures > 0:
                bull_percentage = (total_bull / total_measures) * 100
                print(f"\n📈 État global: {bull_percentage:.1f}% en bull market")
                
                if bull_percentage > 66:
                    print("  🟢 SUPERCYCLE: Accumulation recommandée")
                elif bull_percentage > 33:
                    print("  🟡 MODÉRÉ: Surveillance accrue")
                else:
                    print("  🔴 FAIBLE: Attente ou hedge")
            
            return df
        else:
            print("❌ Aucune donnée Battery Metals")
            return None
    
    def generate_reports(self):
        """Génère des rapports synthétiques"""
        print("\n" + "=" * 70)
        print("📄 GÉNÉRATION DES RAPPORTS")
        print("=" * 70)
        
        try:
            # Rapport texte
            self.generate_text_report()
            
            # Dashboard simple (CSV)
            self.generate_csv_dashboard()
            
            # Fichier de synthèse pour GDELT
            self.generate_gdelt_report()
            
        except Exception as e:
            print(f"❌ Erreur génération rapports: {e}")
    
    def generate_text_report(self):
        """Génère un rapport texte complet"""
        report_path = "rxx_analysis_summary.txt"
        
        cursor = self.conn.cursor()
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write("SYNTHÈSE ANALYSE Rxx Engine\n")
            f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M CET')}\n")
            f.write("=" * 80 + "\n\n")
            
            # 1. Statistiques générales
            f.write("1. STATISTIQUES GÉNÉRALES\n")
            f.write("-" * 40 + "\n")
            
            cursor.execute("SELECT COUNT(*) FROM executions")
            total_exec = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(DISTINCT node_id) FROM rxx_data")
            unique_nodes = cursor.fetchone()[0]
            
            cursor.execute("SELECT AVG(idd_score) FROM executions")
            avg_idd = cursor.fetchone()[0]
            
            f.write(f"Exécutions totales: {total_exec}\n")
            f.write(f"Nœuds uniques suivis: {unique_nodes}\n")
            f.write(f"IDD moyen: {avg_idd:.1f}/100\n\n")
            
            # 2. Dernière exécution
            f.write("2. DERNIÈRE EXÉCUTION\n")
            f.write("-" * 40 + "\n")
            
            query = """
            SELECT e.execution_id, e.start_time, e.idd_score, e.idd_decision,
                   COUNT(rd.node_id) as nodes_retrieved
            FROM executions e
            LEFT JOIN rxx_data rd ON e.execution_id = rd.execution_id
            WHERE e.start_time = (SELECT MAX(start_time) FROM executions)
            GROUP BY e.execution_id
            """
            
            cursor.execute(query)
            last_exec = cursor.fetchone()
            if last_exec:
                f.write(f"ID: {last_exec['execution_id']}\n")
                f.write(f"Heure: {last_exec['start_time']}\n")
                f.write(f"IDD: {last_exec['idd_score']:.1f} → {last_exec['idd_decision']}\n")
                f.write(f"Nœuds récupérés: {last_exec['nodes_retrieved']}\n\n")
            
            # 3. Nœuds critiques (valeurs élevées)
            f.write("3. VALEURS CRITIQUES RÉCENTES\n")
            f.write("-" * 40 + "\n")
            
            query = """
            SELECT node_id, valeur, timestamp, priorite
            FROM rxx_data
            WHERE timestamp >= datetime('now', '-1 day')
            AND valeur > 100
            ORDER BY valeur DESC
            LIMIT 10
            """
            
            cursor.execute(query)
            critical_values = cursor.fetchall()
            
            if critical_values:
                for row in critical_values:
                    f.write(f"{row['node_id']}: {row['valeur']} ({row['priorite']}) - {row['timestamp']}\n")
            else:
                f.write("Aucune valeur critique récente\n")
            f.write("\n")
            
            # 4. Recommandations
            f.write("4. RECOMMANDATIONS\n")
            f.write("-" * 40 + "\n")
            
            # Vérifier IDD tendance
            query = """
            SELECT idd_score, start_time
            FROM executions
            ORDER BY start_time DESC
            LIMIT 3
            """
            
            cursor.execute(query)
            last_three = cursor.fetchall()
            
            if len(last_three) >= 2:
                current_idd = last_three[0]['idd_score']
                prev_idd = last_three[1]['idd_score']
                
                if current_idd < 50:
                    f.write("⚠️  IDD BAS: Surveiller indicateurs critiques\n")
                elif current_idd > 70:
                    f.write("✅ IDD OPTIMAL: Continuer monitoring\n")
                
                if current_idd < prev_idd:
                    f.write("📉 IDD en baisse: Vérifier hypothèses DYNAMO\n")
            
            # Vérifier GDELT
            query = """
            SELECT node_id, valeur
            FROM rxx_data
            WHERE node_id LIKE 'R32%'
            AND timestamp >= datetime('now', '-6 hours')
            ORDER BY valeur DESC
            LIMIT 1
            """
            
            cursor.execute(query)
            latest_gdelt = cursor.fetchone()
            if latest_gdelt and latest_gdelt['valeur'] > 500:
                f.write(f"🌍 GDELT ÉLEVÉ: {latest_gdelt['node_id']}={latest_gdelt['valeur']}\n")
            
            f.write("\n" + "=" * 80 + "\n")
            f.write("FIN DU RAPPORT\n")
        
        print(f"✅ Rapport généré: {report_path}")
    
    def generate_csv_dashboard(self):
        """Génère un dashboard CSV des dernières données"""
        output_path = "rxx_latest_data.csv"
        
        query = """
        SELECT 
            rd.node_id,
            rd.valeur,
            rd.domaine,
            rd.priorite,
            rd.statut_contextuel,
            rd.timestamp,
            e.idd_score,
            e.idd_decision
        FROM rxx_data rd
        JOIN executions e ON rd.execution_id = e.execution_id
        WHERE e.start_time = (SELECT MAX(start_time) FROM executions)
        ORDER BY rd.priorite, rd.node_id
        """
        
        df = pd.read_sql_query(query, self.conn)
        
        if len(df) > 0:
            df.to_csv(output_path, index=False, encoding='utf-8')
            print(f"✅ Dashboard CSV: {output_path} ({len(df)} lignes)")
            
            # Fichier trié par priorité
            priority_order = {'🔴': 0, '🟡': 1, '🟢': 2}
            df['priority_num'] = df['priorite'].map(priority_order)
            df_sorted = df.sort_values('priority_num').drop('priority_num', axis=1)
            
            critical_path = "rxx_critical_nodes.csv"
            critical_nodes = df_sorted[df_sorted['priorite'] == '🔴']
            if len(critical_nodes) > 0:
                critical_nodes.to_csv(critical_path, index=False)
                print(f"✅ Nœuds critiques: {critical_path}")
            
            return df
        else:
            print("❌ Aucune donnée pour le dashboard")
            return None
    
    def generate_gdelt_report(self):
        """Génère un rapport spécifique pour GDELT"""
        report_path = "gdelt_analysis_report.txt"
        
        cursor = self.conn.cursor()
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("=" * 60 + "\n")
            f.write("ANALYSE DONNÉES GDELT\n")
            f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M CET')}\n")
            f.write("=" * 60 + "\n\n")
            
            # Dernières valeurs GDELT
            query = """
            SELECT node_id, valeur, timestamp
            FROM rxx_data
            WHERE node_id LIKE 'R32%'
            AND timestamp >= datetime('now', '-1 day')
            ORDER BY timestamp DESC, node_id
            """
            
            cursor.execute(query)
            gdelt_data = cursor.fetchall()
            
            if gdelt_data:
                f.write("DERNIÈRES VALEURS GDELT (24h):\n")
                f.write("-" * 40 + "\n")
                
                for row in gdelt_data:
                    f.write(f"{row['node_id']}: {row['valeur']} à {row['timestamp']}\n")
                
                f.write("\n")
                
                # Analyse par nœud
                f.write("ANALYSE PAR NŒUD:\n")
                f.write("-" * 40 + "\n")
                
                gdelt_nodes = ['R32', 'R32_17', 'R32_18', 'R32_20']
                for node in gdelt_nodes:
                    query = f"""
                    SELECT AVG(valeur) as moyenne, MAX(valeur) as maximum
                    FROM rxx_data
                    WHERE node_id = ?
                    AND timestamp >= datetime('now', '-7 days')
                    """
                    cursor.execute(query, (node,))
                    avg_val, max_val = cursor.fetchone()
                    
                    if avg_val:
                        f.write(f"{node}:\n")
                        f.write(f"  Moyenne 7j: {avg_val:.1f}\n")
                        f.write(f"  Maximum 7j: {max_val:.1f}\n")
            else:
                f.write("Aucune donnée GDELT récente\n")
            
            f.write("\n" + "=" * 60 + "\n")
            f.write("Source: rxx_history.db\n")
        
        print(f"✅ Rapport GDELT: {report_path}")
    
    def analyze_complete(self):
        """Lance l'analyse complète"""
        if not self.conn:
            return
        
        try:
            # 1. Statistiques générales
            stats = self.get_database_stats()
            
            # 2. Dernières exécutions
            self.analyze_recent_executions(limit=10)
            self.analyze_executions_stats()
            
            # 3. Activité des nœuds
            self.analyze_nodes_activity()
            
            # 4. Données GDELT
            self.analyze_gdelt_data()
            
            # 5. Tendances temporelles (nœuds clés)
            for node in ['R32', 'R15', 'R11', 'R24']:
                self.analyze_temporal_trend(node, days_back=3)
            
            # 6. Hypothèses DYNAMO
            self.analyze_hypotheses_performance()
            
            # 7. Battery Metals
            self.analyze_battery_metals()
            
            # 8. Génération rapports
            self.generate_reports()
            
            print("\n" + "=" * 70)
            print("✅ ANALYSE COMPLÈTE TERMINÉE")
            print("=" * 70)
            print("📁 RAPPORTS GÉNÉRÉS:")
            print("  • rxx_analysis_summary.txt - Synthèse complète")
            print("  • rxx_latest_data.csv - Dashboard des dernières données")
            print("  • rxx_critical_nodes.csv - Nœuds prioritaires")
            print("  • gdelt_analysis_report.txt - Analyse GDELT")
            print(f"\n📊 Base: {stats['total_executions']} exécutions, {stats['unique_nodes']} nœuds")
            print(f"📈 IDD moyen: {stats['avg_idd']:.1f}/100")
            
        except Exception as e:
            print(f"❌ Erreur lors de l'analyse: {e}")
            import traceback
            traceback.print_exc()
        finally:
            if self.conn:
                self.conn.close()

# Interface simple
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        db_path = sys.argv[1]
    else:
        db_path = "rxx_history.db"
    
    analyzer = RxxDatabaseAnalyzerV2(db_path)
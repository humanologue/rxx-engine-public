#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
db_integration.py - Module d'intégration base de données chronologique
✅ Stockage historique des données Rxx - VERSION CORRIGÉE
"""

import sqlite3
import json
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
import logging
from typing import Dict, List, Optional, Any
import hashlib

class RxxDatabase:
    """Classe de gestion de la base de données chronologique Rxx"""
    
    def __init__(self, db_path: str = "rxx_history.db", retention_days: int = 90):
        """
        Initialise la base de données
        
        Args:
            db_path: Chemin vers la base SQLite
            retention_days: Nombre de jours de rétention des données
        """
        self.db_path = Path(db_path)
        self.retention_days = retention_days
        self.logger = self._setup_logger()
        
        # Créer la base si elle n'existe pas
        self._init_database()
        
    def _setup_logger(self):
        """Configure le logger"""
        logger = logging.getLogger('RxxDatabase')
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def _init_database(self):
        """Initialise les tables de la base de données"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Table principale des données
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS rxx_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    node_id TEXT NOT NULL,
                    valeur REAL,
                    valeur_text TEXT,
                    domaine TEXT,
                    priorite TEXT,
                    statut_contextuel TEXT,
                    alerte_seuil TEXT,
                    hypothese_liee TEXT,
                    statut_exec TEXT,
                    seuil TEXT,
                    timestamp DATETIME NOT NULL,
                    execution_id TEXT NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(node_id, execution_id)
                )
            ''')
            
            # Table des métadonnées d'exécution
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS executions (
                    execution_id TEXT PRIMARY KEY,
                    total_nodes INTEGER,
                    scripts_executed INTEGER,
                    numerical_values INTEGER,
                    hypotheses_ok INTEGER,
                    hypotheses_total INTEGER,
                    battery_bull INTEGER,
                    battery_total INTEGER,
                    idd_score REAL,
                    idd_decision TEXT,
                    start_time DATETIME,
                    end_time DATETIME,
                    duration_seconds REAL,
                    status TEXT
                )
            ''')
            
            # Table des hypothèses
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS hypotheses (
                    execution_id TEXT,
                    hypothesis_id TEXT,
                    resultat TEXT,
                    details TEXT,
                    condition TEXT,
                    FOREIGN KEY (execution_id) REFERENCES executions (execution_id),
                    UNIQUE(execution_id, hypothesis_id)
                )
            ''')
            
            # Table des métaux battery
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS battery_metals (
                    execution_id TEXT,
                    node_id TEXT,
                    metal TEXT,
                    valeur REAL,
                    seuil REAL,
                    unite TEXT,
                    statut TEXT,
                    bull BOOLEAN,
                    FOREIGN KEY (execution_id) REFERENCES executions (execution_id),
                    UNIQUE(execution_id, node_id)
                )
            ''')
            
            # Index pour les requêtes temporelles
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_rxx_data_timestamp ON rxx_data(timestamp)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_rxx_data_node ON rxx_data(node_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_executions_time ON executions(start_time)')
            
            conn.commit()
        
        self.logger.info(f"Base de données initialisée : {self.db_path}")
    
    def _generate_execution_id(self, timestamp: datetime = None) -> str:
        """Génère un ID unique pour l'exécution"""
        if timestamp is None:
            timestamp = datetime.now()
        
        # Format: YYYYMMDD_HHMMSS_hash
        base = timestamp.strftime("%Y%m%d_%H%M%S")
        random_hash = hashlib.md5(str(timestamp.timestamp()).encode()).hexdigest()[:8]
        return f"{base}_{random_hash}"
    
    def store_execution(self, donnees_enhanced: Dict, hypotheses: Dict, 
                       battery_matrix: Dict, idd: Dict, metadata: Dict = None) -> str:
        """
        Stocke une exécution complète dans la base
        
        Args:
            donnees_enhanced: Données enrichies du CSV
            hypotheses: Résultats des hypothèses
            battery_matrix: Matrice des métaux battery
            idd: Résultats IDD
            metadata: Métadonnées supplémentaires
            
        Returns:
            execution_id: ID de l'exécution stockée
        """
        execution_id = self._generate_execution_id()
        start_time = datetime.now()
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 1. Stocker les données des nœuds
                for node_id, data in donnees_enhanced.items():
                    # Convertir la valeur en numérique si possible
                    valeur_num = None
                    valeur_text = str(data.get('valeur_live', ''))
                    
                    try:
                        valeur_num = float(str(valeur_text).replace(',', '.'))
                    except (ValueError, TypeError):
                        valeur_num = None
                    
                    # Nettoyer le timestamp (supprimer ' CET')
                    timestamp_str = str(data.get('timestamp', start_time))
                    timestamp_clean = timestamp_str.replace(' CET', '')
                    
                    cursor.execute('''
                        INSERT OR REPLACE INTO rxx_data 
                        (node_id, valeur, valeur_text, domaine, priorite, 
                         statut_contextuel, alerte_seuil, hypothese_liee, 
                         statut_exec, seuil, timestamp, execution_id)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        node_id,
                        valeur_num,
                        valeur_text,
                        data.get('domaine', ''),
                        data.get('priorite', ''),
                        data.get('statut_contextuel', ''),
                        data.get('alerte_seuil', ''),
                        data.get('hypothese_liee', ''),
                        data.get('statut_exec', ''),
                        data.get('seuil', ''),
                        timestamp_clean,
                        execution_id
                    ))
                
                # 2. Stocker les métadonnées d'exécution
                metadata = metadata or {}
                cursor.execute('''
                    INSERT INTO executions 
                    (execution_id, total_nodes, scripts_executed, numerical_values,
                     hypotheses_ok, hypotheses_total, battery_bull, battery_total,
                     idd_score, idd_decision, start_time, end_time, duration_seconds, status)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    execution_id,
                    metadata.get('total_nodes', len(donnees_enhanced)),
                    metadata.get('scripts_executed', len([d for d in donnees_enhanced.values() 
                                                         if d.get('statut_exec') not in ['MANUEL', 'NO_FILE']])),
                    metadata.get('numerical_values', len([d for d in donnees_enhanced.values() 
                                                         if str(d.get('valeur_live', '')).replace('.', '').replace(',', '').isdigit()])),
                    idd.get('ok', 0),
                    idd.get('hypotheses_evaluees', 0),
                    battery_matrix.get('bull_count', 0),
                    battery_matrix.get('total', 0),
                    idd.get('score', 0),
                    idd.get('decision', ''),
                    start_time,
                    datetime.now(),
                    (datetime.now() - start_time).total_seconds(),
                    'COMPLETED'
                ))
                
                # 3. Stocker les hypothèses
                for hyp_id, data in hypotheses.items():
                    cursor.execute('''
                        INSERT INTO hypotheses (execution_id, hypothesis_id, resultat, details, condition)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (
                        execution_id,
                        hyp_id,
                        data.get('resultat', ''),
                        data.get('details', ''),
                        data.get('condition', '')
                    ))
                
                # 4. Stocker les métaux battery
                for node_id, metal_info in battery_matrix.get('details', {}).items():
                    cursor.execute('''
                        INSERT INTO battery_metals 
                        (execution_id, node_id, metal, valeur, seuil, unite, statut, bull)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        execution_id,
                        node_id,
                        metal_info.get('metal', ''),
                        metal_info.get('valeur', 0),
                        metal_info.get('seuil', 0),
                        metal_info.get('unite', ''),
                        metal_info.get('statut', ''),
                        1 if metal_info.get('bull', False) else 0
                    ))
                
                conn.commit()
                
                # 5. Nettoyer les anciennes données
                self._clean_old_data()
                
                self.logger.info(f"Exécution stockée : {execution_id} - {len(donnees_enhanced)} nœuds")
                return execution_id
                
        except Exception as e:
            self.logger.error(f"Erreur lors du stockage : {e}")
            raise
    
    def _clean_old_data(self):
        """Nettoie les données plus vieilles que la période de rétention"""
        cutoff_date = datetime.now() - timedelta(days=self.retention_days)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Supprimer les données anciennes
            cursor.execute("DELETE FROM rxx_data WHERE timestamp < ?", (cutoff_date,))
            deleted_rows = cursor.rowcount
            
            # Supprimer les exécutions orphelines
            cursor.execute('''
                DELETE FROM executions WHERE execution_id NOT IN 
                (SELECT DISTINCT execution_id FROM rxx_data)
            ''')
            
            conn.commit()
            
            if deleted_rows > 0:
                self.logger.info(f"Nettoyage : {deleted_rows} lignes supprimées (avant {cutoff_date})")
    
    # ============================================================================
    # MÉTHODES DE REQUÊTE (CORRIGÉES)
    # ============================================================================
    
    def get_node_history(self, node_id: str, days: int = 30) -> pd.DataFrame:
        """
        Récupère l'historique d'un nœud spécifique
        
        Args:
            node_id: Identifiant du nœud (ex: 'R11')
            days: Nombre de jours d'historique
            
        Returns:
            DataFrame avec l'historique du nœud
        """
        cutoff_date = datetime.now() - timedelta(days=days)
        
        query = '''
            SELECT 
                d.timestamp,
                d.valeur,
                d.valeur_text,
                d.statut_contextuel,
                d.alerte_seuil,
                e.idd_score,
                e.idd_decision
            FROM rxx_data d
            JOIN executions e ON d.execution_id = e.execution_id
            WHERE d.node_id = ? AND d.timestamp >= ?
            ORDER BY d.timestamp ASC
        '''
        
        with sqlite3.connect(self.db_path) as conn:
            df = pd.read_sql_query(query, conn, params=(node_id, cutoff_date))
        
        if not df.empty:
            # Corrigé : gérer le timezone CET
            df['timestamp'] = pd.to_datetime(df['timestamp'].str.replace(' CET', ''), errors='coerce')
            df['valeur'] = pd.to_numeric(df['valeur'], errors='coerce')
        
        return df
    
    def get_last_n_executions(self, n: int = 10) -> pd.DataFrame:
        """Récupère les N dernières exécutions"""
        query = '''
            SELECT 
                execution_id,
                start_time,
                end_time,
                duration_seconds,
                total_nodes,
                scripts_executed,
                numerical_values,
                hypotheses_ok,
                hypotheses_total,
                battery_bull,
                battery_total,
                idd_score,
                idd_decision,
                status
            FROM executions
            ORDER BY start_time DESC
            LIMIT ?
        '''
        
        with sqlite3.connect(self.db_path) as conn:
            df = pd.read_sql_query(query, conn, params=(n,))
        
        if not df.empty:
            df['start_time'] = pd.to_datetime(df['start_time'])
            df['end_time'] = pd.to_datetime(df['end_time'])
            df['success_rate'] = (df['scripts_executed'] / df['total_nodes']) * 100
        
        return df
    
    def get_hypothesis_trend(self, hypothesis_id: str, days: int = 30) -> pd.DataFrame:
        """Récupère l'historique d'une hypothèse spécifique"""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        query = '''
            SELECT 
                e.start_time,
                h.resultat,
                h.details
            FROM hypotheses h
            JOIN executions e ON h.execution_id = e.execution_id
            WHERE h.hypothesis_id = ? AND e.start_time >= ?
            ORDER BY e.start_time ASC
        '''
        
        with sqlite3.connect(self.db_path) as conn:
            df = pd.read_sql_query(query, conn, params=(hypothesis_id, cutoff_date))
        
        if not df.empty:
            df['start_time'] = pd.to_datetime(df['start_time'])
            # Convertir les résultats en scores
            result_scores = {'✅': 1, '🟢': 1, '🟡': 0.5, '⚠️': 0.5, '⚪': 0.25, '❌': 0}
            df['score'] = df['resultat'].map(result_scores).fillna(0)
        
        return df
    
    def get_battery_metals_history(self, days: int = 30) -> Dict[str, pd.DataFrame]:
        """Récupère l'historique de tous les métaux battery"""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        query = '''
            SELECT 
                b.execution_id,
                b.node_id,
                b.metal,
                b.valeur,
                b.seuil,
                b.unite,
                b.statut,
                b.bull,
                e.start_time
            FROM battery_metals b
            JOIN executions e ON b.execution_id = e.execution_id
            WHERE e.start_time >= ?
            ORDER BY e.start_time ASC, b.node_id
        '''
        
        with sqlite3.connect(self.db_path) as conn:
            df_all = pd.read_sql_query(query, conn, params=(cutoff_date,))
        
        if df_all.empty:
            return {}
        
        df_all['start_time'] = pd.to_datetime(df_all['start_time'])
        
        # Séparer par métal
        result = {}
        for metal in df_all['metal'].unique():
            result[metal] = df_all[df_all['metal'] == metal].copy()
        
        return result
    
    def get_alerts_history(self, days: int = 7) -> pd.DataFrame:
        """Récupère l'historique des alertes (🚨)"""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        query = '''
            SELECT 
                d.timestamp,
                d.node_id,
                d.valeur_text,
                d.valeur,
                d.statut_contextuel,
                d.alerte_seuil,
                d.domaine,
                d.priorite,
                e.idd_score,
                e.idd_decision
            FROM rxx_data d
            JOIN executions e ON d.execution_id = e.execution_id
            WHERE d.alerte_seuil = '🚨' AND d.timestamp >= ?
            ORDER BY d.timestamp DESC, d.priorite
        '''
        
        with sqlite3.connect(self.db_path) as conn:
            df = pd.read_sql_query(query, conn, params=(cutoff_date,))
        
        if not df.empty:
            # Corrigé : gérer le timezone CET
            df['timestamp'] = pd.to_datetime(df['timestamp'].str.replace(' CET', ''), errors='coerce')
        
        return df
    
    # ============================================================================
    # MÉTHODES D'ANALYSE
    # ============================================================================
    
    def calculate_trends(self, node_id: str, days: int = 30) -> Dict:
        """Calcule les tendances pour un nœud spécifique"""
        df = self.get_node_history(node_id, days)
        
        if df.empty or len(df) < 2:
            return {"error": "Données insuffisantes pour l'analyse"}
        
        # Calculs statistiques
        values = pd.to_numeric(df['valeur'], errors='coerce').dropna()
        
        if len(values) < 2:
            return {"error": "Valeurs numériques insuffisantes"}
        
        stats = {
            "current": float(values.iloc[-1]) if not values.empty else None,
            "mean": float(values.mean()),
            "std": float(values.std()),
            "min": float(values.min()),
            "max": float(values.max()),
            "trend": self._calculate_trend_direction(values),
            "volatility": float(values.std() / values.mean() * 100) if values.mean() != 0 else 0,
            "data_points": len(values),
            "period_days": days
        }
        
        # Détection d'anomalies
        stats["anomalies"] = self._detect_anomalies(values)
        
        return stats
    
    def _calculate_trend_direction(self, series: pd.Series) -> str:
        """Détermine la direction de la tendance"""
        if len(series) < 3:
            return "INSUFFICIENT_DATA"
        
        # Régression linéaire simple
        x = list(range(len(series)))
        y = series.values
        
        # Calcul de la pente
        n = len(x)
        sum_x = sum(x)
        sum_y = sum(y)
        sum_xy = sum(x[i] * y[i] for i in range(n))
        sum_x2 = sum(x_i * x_i for x_i in x)
        
        try:
            slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
            
            if slope > 0.1:
                return "↗️ HAUSSIER"
            elif slope < -0.1:
                return "↘️ BAISSIER"
            else:
                return "➡️ STABLE"
        except:
            return "UNKNOWN"
    
    def _detect_anomalies(self, series: pd.Series, threshold: float = 2.0) -> List[Dict]:
        """Détecte les valeurs anormales"""
        if len(series) < 5:
            return []
        
        mean = series.mean()
        std = series.std()
        
        anomalies = []
        for i, value in enumerate(series):
            z_score = abs((value - mean) / std) if std != 0 else 0
            if z_score > threshold:
                anomalies.append({
                    "index": i,
                    "value": float(value),
                    "z_score": float(z_score),
                    "timestamp": series.index[i] if hasattr(series, 'index') else i
                })
        
        return anomalies
    
    def generate_dashboard_data(self, days: int = 30) -> Dict:
        """Génère les données pour un dashboard - CORRIGÉE"""
        dashboard = {
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "period_days": days,
                "database_size": self.db_path.stat().st_size if self.db_path.exists() else 0
            },
            "summary": {},
            "trends": {},
            "alerts": {},
            "hypotheses_trends": {}  # CLAJ AJOUTÉE ICI
        }
        
        # Récupérer les dernières exécutions
        last_executions = self.get_last_n_executions(10)
        if not last_executions.empty:
            dashboard["summary"]["last_executions"] = last_executions.to_dict('records')
            dashboard["summary"]["avg_idd"] = float(last_executions['idd_score'].mean())
            dashboard["summary"]["success_rate"] = float(last_executions['success_rate'].mean())
        
        # Nœuds critiques pour le dashboard
        critical_nodes = ['R00', 'R01', 'R02', 'R11', 'R24', 'R65', 'R81', 'R91']
        for node_id in critical_nodes:
            trends = self.calculate_trends(node_id, min(days, 7))  # 7 jours pour les tendances courtes
            if "error" not in trends:
                dashboard["trends"][node_id] = trends
        
        # Alertes récentes
        alerts = self.get_alerts_history(7)
        if not alerts.empty:
            dashboard["alerts"]["recent"] = alerts.to_dict('records')
            dashboard["alerts"]["count_by_domain"] = alerts.groupby('domaine').size().to_dict()
        
        # Tendances des hypothèses
        for hyp_id in ['H1_P4', 'H2_OTAN', 'H3_CYBER_SUPPLY', 'H6_CH_Afrique']:
            trend_df = self.get_hypothesis_trend(hyp_id, days)
            if not trend_df.empty:
                dashboard["hypotheses_trends"][hyp_id] = {
                    "current": trend_df.iloc[-1]['resultat'] if not trend_df.empty else "N/A",
                    "history": trend_df.to_dict('records')
                }
        
        return dashboard
    
    def export_to_json(self, output_path: str = "rxx_history_export.json"):
        """Exporte les données récentes en JSON"""
        dashboard_data = self.generate_dashboard_data(30)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(dashboard_data, f, indent=2, ensure_ascii=False, default=str)
        
        self.logger.info(f"Données exportées vers : {output_path}")
        return output_path

# ============================================================================
# INTÉGRATION AVEC RXX ENGINE V17.0 - VERSION CORRIGÉE
# ============================================================================

def integrate_with_engine_v17():
    """
    Fonction d'intégration avec le script r_dynamo.py V17.0
    """
    import sys
    from pathlib import Path
    
    # Importer les données générées par V17.0
    data_dir = Path.cwd()
    
    try:
        # Charger les fichiers générés
        with open(data_dir / "validation_report.json", 'r', encoding='utf-8') as f:
            validation_report = json.load(f)
        
        with open(data_dir / "hypotheses_check.json", 'r', encoding='utf-8') as f:
            hypotheses = json.load(f)
        
        # Charger CSV enrichi
        df_enhanced = pd.read_csv(data_dir / "monitoring_enhanced.csv", sep=';')
        
        # Convertir en format dict pour la base
        donnees_enhanced = {}
        for _, row in df_enhanced.iterrows():
            donnees_enhanced[row['node_id']] = row.to_dict()
        
        # Initialiser la base de données
        db = RxxDatabase()
        
        # Stocker l'exécution
        execution_id = db.store_execution(
            donnees_enhanced=donnees_enhanced,
            hypotheses=hypotheses,
            battery_matrix=validation_report['battery_metals'],
            idd=validation_report['idd'],
            metadata=validation_report['statistiques']
        )
        
        # Générer un rapport d'analyse
        dashboard = db.generate_dashboard_data(7)
        
        # Export JSON
        export_file = db.export_to_json()
        
        print(f"   ✅ Intégration réussie : {execution_id}")
        return True  # <-- CHANGEMENT CRITIQUE ICI !
        
    except FileNotFoundError as e:
        print(f"   ⚠️  Fichier manquant : {e}")
        return False
    except Exception as e:
        print(f"   ❌ Erreur d'intégration : {e}")
        import traceback
        traceback.print_exc()
        return False
# ============================================================================
# FONCTION SIMPLIFIÉE POUR INTÉGRATION
# ============================================================================
def simple_integration():
    """
    Version simplifiée pour intégration directe dans r_dynamo.py
    """
    try:
        print("   📦 Début de l'intégration...")
        
        # Désactiver les logs
        import logging
        original_level = logging.getLogger('RxxDatabase').level
        logging.getLogger('RxxDatabase').setLevel(logging.WARNING)
        
        # Appeler l'intégration principale
        result = integrate_with_engine_v17()
        
        print(f"   🔍 Résultat brut: {type(result)}")
        
        # Vérifier le résultat différemment
        if result:
            print(f"   ✅ integrate_with_engine_v17() a retourné quelque chose")
            
            # Essayer d'extraire l'execution_id de différentes manières
            exec_id = None
            
            if isinstance(result, dict) and 'execution_id' in result:
                exec_id = result['execution_id']
            elif isinstance(result, tuple) and len(result) >= 2:
                # Si c'est un tuple (db, execution_id)
                exec_id = result[1] if len(result) > 1 else None
            
            if exec_id:
                print(f"   ✅ Exécution stockée : {exec_id}")
                
                # Compter les exécutions
                import sqlite3
                conn = sqlite3.connect("rxx_history.db")
                count = conn.execute("SELECT COUNT(*) FROM executions").fetchone()[0]
                conn.close()
                
                print(f"   📊 Base : rxx_history.db")
                print(f"   📈 Total exécutions : {count}")
                
                if isinstance(result, dict) and result.get('export_file'):
                    print(f"   💾 Export : {result['export_file']}")
                
                # Réactiver les logs
                logging.getLogger('RxxDatabase').setLevel(original_level)
                
                return True
            else:
                print(f"   ⚠️  Pas d'execution_id trouvé dans le résultat")
                print(f"   📋 Format résultat: {type(result)}")
                if isinstance(result, dict):
                    print(f"   📋 Clés: {list(result.keys())}")
                elif isinstance(result, tuple):
                    print(f"   📋 Longueur tuple: {len(result)}")
        else:
            print("   ⚠️  integrate_with_engine_v17() a retourné None ou False")
            
        # Réactiver les logs
        logging.getLogger('RxxDatabase').setLevel(original_level)
        return False
            
    except ImportError as e:
        print(f"   ⚠️  Module db_integration non disponible: {e}")
        return False
    except Exception as e:
        print(f"   ⚠️  Erreur : {str(e)[:100]}")
        import traceback
        traceback.print_exc()
        return False
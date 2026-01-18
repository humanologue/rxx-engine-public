# dashboard_interactive.py - VERSION CORRIGÉE
import json
from datetime import datetime

def create_fixed_dashboard():
    """Crée un dashboard interactif avec les données ACTUELLES"""
    try:
        # Lire les données ACTUELLES
        with open('validation_report.json', 'r', encoding='utf-8') as f:
            v_report = json.load(f)
        
        with open('hypotheses_check.json', 'r', encoding='utf-8') as f:
            hypotheses = json.load(f)
        
        # Extraire les données avec des valeurs par défaut
        idd_score = v_report.get('idd', {}).get('score', 0)
        idd_decision = v_report.get('idd', {}).get('decision', 'N/A')
        
        battery_metals = v_report.get('battery_metals', {})
        battery_bull = battery_metals.get('bull_count', 0)
        battery_total = battery_metals.get('total', 6)
        battery_recommendation = battery_metals.get('recommendation', '⚠️ MODÉRÉ')
        
        stats = v_report.get('statistiques', {})
        total_nodes = stats.get('total_nodes', 0)
        
        # Compter les hypothèses OK
        ok_count = 0
        for h in hypotheses.values():
            result = h.get('resultat', '')
            if result in ['✅', '🟢', '⚪']:  # Ajoutez les statuts que vous considérez comme OK
                ok_count += 1
        
        # HTML corrigé
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Rxx Engine V17.0 - Dashboard CORRIGÉ</title>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body {{
                    font-family: 'Segoe UI', Arial, sans-serif;
                    margin: 0;
                    padding: 20px;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    min-height: 100vh;
                }}
                
                .container {{
                    max-width: 1200px;
                    margin: 0 auto;
                    background: white;
                    border-radius: 20px;
                    padding: 30px;
                    box-shadow: 0 20px 60px rgba(0,0,0,0.3);
                }}
                
                .header {{
                    text-align: center;
                    margin-bottom: 40px;
                    padding-bottom: 20px;
                    border-bottom: 3px solid #f0f0f0;
                }}
                
                .header h1 {{
                    color: #2c3e50;
                    margin: 0;
                    font-size: 2.5em;
                }}
                
                .header p {{
                    color: #7f8c8d;
                    font-size: 1.1em;
                }}
                
                .stats-grid {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                    gap: 25px;
                    margin-bottom: 40px;
                }}
                
                .stat-card {{
                    background: linear-gradient(145deg, #ffffff, #f8f9fa);
                    border-radius: 15px;
                    padding: 25px;
                    text-align: center;
                    box-shadow: 0 10px 30px rgba(0,0,0,0.1);
                    transition: transform 0.3s, box-shadow 0.3s;
                    border: 2px solid transparent;
                }}
                
                .stat-card:hover {{
                    transform: translateY(-5px);
                    box-shadow: 0 15px 40px rgba(0,0,0,0.2);
                }}
                
                .stat-card.idd {{
                    border-color: #f39c12;
                }}
                
                .stat-card.hypotheses {{
                    border-color: #27ae60;
                }}
                
                .stat-card.battery {{
                    border-color: #3498db;
                }}
                
                .stat-card.nodes {{
                    border-color: #9b59b6;
                }}
                
                .stat-card h3 {{
                    color: #2c3e50;
                    margin-top: 0;
                    font-size: 1.2em;
                    margin-bottom: 15px;
                }}
                
                .big-number {{
                    font-size: 3.5em;
                    font-weight: bold;
                    margin: 10px 0;
                    background: linear-gradient(45deg, #667eea, #764ba2);
                    -webkit-background-clip: text;
                    -webkit-text-fill-color: transparent;
                }}
                
                .decision {{
                    font-size: 1.3em;
                    font-weight: bold;
                    margin-top: 10px;
                    padding: 8px 15px;
                    border-radius: 25px;
                    display: inline-block;
                }}
                
                .decision.surveillance {{
                    background: #fef5e7;
                    color: #f39c12;
                }}
                
                .decision.moderate {{
                    background: #e8f6f3;
                    color: #27ae60;
                }}
                
                .percentage {{
                    font-size: 1.5em;
                    color: #2c3e50;
                    margin-top: 5px;
                }}
                
                .subtext {{
                    color: #7f8c8d;
                    font-size: 0.9em;
                    margin-top: 10px;
                }}
                
                .hypotheses-table {{
                    width: 100%;
                    border-collapse: collapse;
                    margin: 30px 0;
                    border-radius: 10px;
                    overflow: hidden;
                    box-shadow: 0 5px 15px rgba(0,0,0,0.1);
                }}
                
                .hypotheses-table th {{
                    background: linear-gradient(45deg, #667eea, #764ba2);
                    color: white;
                    padding: 15px;
                    text-align: left;
                    font-weight: 600;
                }}
                
                .hypotheses-table td {{
                    padding: 15px;
                    border-bottom: 1px solid #f0f0f0;
                }}
                
                .hypotheses-table tr:hover {{
                    background-color: #f8f9fa;
                }}
                
                .result-icon {{
                    font-size: 1.8em;
                    text-align: center;
                }}
                
                .info-box {{
                    background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
                    border-radius: 15px;
                    padding: 25px;
                    margin-top: 40px;
                }}
                
                .info-box h3 {{
                    color: #2c3e50;
                    margin-top: 0;
                }}
                
                .info-box p {{
                    color: #34495e;
                    line-height: 1.6;
                }}
                
                .timestamp {{
                    text-align: center;
                    margin-top: 30px;
                    color: #7f8c8d;
                    font-size: 0.9em;
                }}
                
                @media (max-width: 768px) {{
                    .stats-grid {{
                        grid-template-columns: 1fr;
                    }}
                    
                    .container {{
                        padding: 15px;
                    }}
                    
                    .header h1 {{
                        font-size: 1.8em;
                    }}
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🚀 Rxx Engine V17.0 - Dashboard Interactif</h1>
                    <p>📊 Surveillance géopolitique et économique en temps réel</p>
                </div>
                
                <div class="stats-grid">
                    <!-- IDD ACTUEL -->
                    <div class="stat-card idd">
                        <h3>🎯 Indice de Décision Dynamique</h3>
                        <div class="big-number">{idd_score}</div>
                        <div class="decision surveillance">{idd_decision}</div>
                        <div class="subtext">Score sur 100 points</div>
                    </div>
                    
                    <!-- HYPOTHÈSES ACTUELLES -->
                    <div class="stat-card hypotheses">
                        <h3>✅ Hypothèses Validées</h3>
                        <div class="big-number">{ok_count}/8</div>
                        <div class="percentage">{int(ok_count/8*100) if 8 > 0 else 0}%</div>
                        <div class="subtext">Sur 8 hypothèses stratégiques</div>
                    </div>
                    
                    <!-- BATTERY METALS ACTUELS -->
                    <div class="stat-card battery">
                        <h3>🔋 Battery Metals</h3>
                        <div class="big-number">{battery_bull}/{battery_total}</div>
                        <div class="decision moderate">{battery_recommendation}</div>
                        <div class="subtext">Métaux critiques en bull market</div>
                    </div>
                    
                    <!-- NŒUDS -->
                    <div class="stat-card nodes">
                        <h3>📊 Nœuds Surveillés</h3>
                        <div class="big-number">{total_nodes}</div>
                        <div class="subtext">Indicateurs en temps réel</div>
                    </div>
                </div>
                
                <h2 style="color: #2c3e50; margin-top: 40px;">📋 Détails des Hypothèses</h2>
                <table class="hypotheses-table">
                    <tr>
                        <th>Hypothèse</th>
                        <th>Résultat</th>
                        <th>Détails</th>
                        <th>Condition</th>
                    </tr>
        """
        
        # Ajouter les lignes des hypothèses
        for hyp_id, data in hypotheses.items():
            result_icon = data.get('resultat', '❓')
            details = data.get('details', 'N/A')
            condition = data.get('condition', 'N/A')
            
            # Couleur basée sur le résultat
            result_color = ""
            if '✅' in result_icon or '🟢' in result_icon:
                result_color = "color: #27ae60;"
            elif '⚪' in result_icon or '🟡' in result_icon or '⚠️' in result_icon:
                result_color = "color: #f39c12;"
            elif '❌' in result_icon:
                result_color = "color: #e74c3c;"
            
            html += f"""
                    <tr>
                        <td><strong>{hyp_id}</strong></td>
                        <td class="result-icon" style="{result_color}">{result_icon}</td>
                        <td>{details}</td>
                        <td><small>{condition}</small></td>
                    </tr>
            """
        
        html += f"""
                </table>
                
                <div class="info-box">
                    <h3>🔍 Informations Techniques</h3>
                    <p><strong>📅 Dernière exécution :</strong> {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}</p>
                    <p><strong>📁 Source des données :</strong> Dernière exécution complète V17.0</p>
                    <p><strong>💾 Base de données :</strong> 27 exécutions historiques stockées</p>
                    <p><strong>🎯 Objectif :</strong> Fournir une vue temps réel de la situation géopolitique et économique</p>
                    <p><strong>⚠️ Note :</strong> Ce dashboard affiche les données de la dernière exécution, pas une moyenne historique.</p>
                </div>
                
                <div class="timestamp">
                    <p>🔄 Système Rxx Engine V17.0 - Généré automatiquement</p>
                    <p>📧 Pour toute question : système@rxx-engine.fr</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Écrire le fichier
        output_file = 'dashboard_interactive.html'
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html)
        
        print(f"✅ Dashboard interactif généré : {output_file}")
        print(f"   📊 Statistiques actuelles :")
        print(f"      • IDD: {idd_score}/100 → {idd_decision}")
        print(f"      • Hypothèses: {ok_count}/8 validées ({int(ok_count/8*100)}%)")
        print(f"      • Battery Metals: {battery_bull}/{battery_total} en bull")
        print(f"      • Nœuds: {total_nodes} surveillés")
        print(f"\n   🌐 Ouvrez le fichier dans votre navigateur :")
        print(f"      start {output_file}")
        
        return output_file
        
    except FileNotFoundError as e:
        print(f"❌ Fichier non trouvé : {e}")
        print("   Assurez-vous d'avoir exécuté 'python r_dynamo.py' d'abord")
        return None
    except json.JSONDecodeError as e:
        print(f"❌ Erreur JSON : {e}")
        print("   Les fichiers de rapport sont peut-être corrompus")
        return None
    except Exception as e:
        print(f"❌ Erreur inattendue : {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    html_file = create_fixed_dashboard()
    if html_file:
        # Ouvrir automatiquement dans le navigateur
        import webbrowser
        webbrowser.open(html_file)
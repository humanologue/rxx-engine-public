# plotly_dashboard.py
import plotly.graph_objects as go
import sqlite3
import pandas as pd

def generate_idd_history_chart(db_path="rxx_history.db"):
    """Génère un graphique de l'historique IDD"""
    conn = sqlite3.connect(db_path)
    df = pd.read_sql_query("""
        SELECT start_time, idd_score, total_nodes 
        FROM executions 
        ORDER BY start_time DESC 
        LIMIT 30
    """, conn)
    conn.close()
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df['start_time'], y=df['idd_score'],
        mode='lines+markers',
        name='IDD Score',
        line=dict(color='blue', width=2)
    ))
    
    # Ajouter des zones
    fig.add_hrect(y0=75, y1=100, line_width=0, 
                  fillcolor="green", opacity=0.1, 
                  annotation_text="OPTIMAL", annotation_position="top left")
    fig.add_hrect(y0=50, y1=75, line_width=0, 
                  fillcolor="yellow", opacity=0.1,
                  annotation_text="SURVEILLANCE", annotation_position="top left")
    fig.add_hrect(y0=0, y1=50, line_width=0, 
                  fillcolor="red", opacity=0.1,
                  annotation_text="ALERTE", annotation_position="top left")
    
    fig.update_layout(
        title='Historique IDD (30 dernières exécutions)',
        xaxis_title='Date/Heure',
        yaxis_title='Score IDD',
        template='plotly_white'
    )
    
    return fig.to_html(full_html=False)
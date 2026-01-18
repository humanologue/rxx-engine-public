# dashboard_simple.py
import sqlite3
import pandas as pd

conn = sqlite3.connect("rxx_history.db")
df = pd.read_sql_query("""
    SELECT 
        execution_id,
        DATE(start_time) as date,
        idd_score,
        total_nodes,
        hypotheses_ok * 100.0 / hypotheses_total as hypotheses_rate
    FROM executions 
    ORDER BY start_time DESC
    LIMIT 10
""", conn)

print("📊 DERNIÈRES 10 EXÉCUTIONS :")
print(df.to_string())
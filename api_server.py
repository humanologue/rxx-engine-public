# api_server.py
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
import json
import uvicorn

app = FastAPI(title="Rxx Engine API", version="1.0")

@app.get("/", response_class=HTMLResponse)
def read_root():
    return """
    <html>
        <body>
            <h1>Rxx Engine API V1.0</h1>
            <p>Endpoints disponibles:</p>
            <ul>
                <li><a href="/api/status">/api/status</a> - Statut actuel</li>
                <li><a href="/api/history">/api/history</a> - Historique IDD</li>
                <li><a href="/api/nodes">/api/nodes</a> - Valeurs des nœuds</li>
            </ul>
        </body>
    </html>
    """

@app.get("/api/status")
def get_status():
    try:
        with open("validation_report.json", "r") as f:
            return json.load(f)
    except:
        raise HTTPException(status_code=404, detail="Rapport non disponible")

@app.get("/api/hypotheses")
def get_hypotheses():
    try:
        with open("hypotheses_check.json", "r") as f:
            return json.load(f)
    except:
        raise HTTPException(status_code=404, detail="Hypothèses non disponibles")

# Pour lancer: uvicorn api_server:app --reload --host 0.0.0.0 --port 8000
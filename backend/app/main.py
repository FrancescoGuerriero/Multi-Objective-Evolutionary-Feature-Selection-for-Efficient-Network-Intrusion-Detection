"""Local-only FastAPI read-only dashboard for EvoNIDS research and Windows telemetry.

Run uvicorn on 127.0.0.1; deliberately no remote capture or firewall endpoints.
"""
from __future__ import annotations

import csv
import json
from collections import deque
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from prototype.telemetry import event_to_dict, snapshot_connections

ROOT = Path(__file__).resolve().parents[2]
ALERTS = ROOT / "results" / "alerts.jsonl"
SUMMARY = ROOT / "results" / "final_summary.csv"

app = FastAPI(title="EvoNIDS — Local Defensive IDS Dashboard", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=False,
    allow_methods=["GET"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok", "scope": "localhost-only, read-only", "live_ml_classification": False}


@app.get("/api/project")
def project():
    return {
        "title": "Multi-Objective Evolutionary Feature Selection for Efficient Network Intrusion Detection",
        "algorithms": ["GA", "BPSO", "PSO", "NSGA-II"],
        "classifiers": ["Logistic Regression", "Random Forest", "XGBoost"],
        "default_repeated_runs": 5,
        "status": "Research evidence + passive Windows prototype",
    }


@app.get("/api/data/status")
def data_status():
    train = ROOT / "data/raw/UNSW_NB15_training-set.csv"
    test = ROOT / "data/raw/UNSW_NB15_testing-set.csv"
    return {
        "train_expected": str(train.relative_to(ROOT)),
        "test_expected": str(test.relative_to(ROOT)),
        "train_present": train.is_file(),
        "test_present": test.is_file(),
        "ready_for_baselines": train.is_file() and test.is_file(),
    }


@app.get("/api/ids/status")
def ids_status():
    return {
        "windows_socket_monitor": "passive", "socket_ml_inference": False,
        "compatible_flow_csv_inference": "CLI watch-flows / replay",
        "alerts_present": ALERTS.is_file(),
        "notice": "Socket metadata does not contain the engineered UNSW-NB15 features."
    }


@app.get("/api/ids/connections")
def connections():
    records = [event_to_dict(event) for event in snapshot_connections()]
    return {"count": len(records), "connections": records[:250], "truncated": len(records) > 250}


@app.get("/api/ids/alerts")
def alerts():
    if not ALERTS.exists():
        return {"count": 0, "alerts": [], "source": str(ALERTS.relative_to(ROOT))}
    # Read only last 100 complete lines; skip malformed lines produced by interrupted writers.
    with ALERTS.open("r", encoding="utf-8") as stream:
        lines = deque(stream, maxlen=100)
    parsed = []
    for line in lines:
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(event, dict) and event.get("source") == "compatible_flow_csv":
            parsed.append(event)
    return {"count": len(parsed), "alerts": list(reversed(parsed)),
            "source": str(ALERTS.relative_to(ROOT))}


@app.get("/api/research/comparison")
def research_comparison():
    if not SUMMARY.is_file():
        return {"methods": [], "source": str(SUMMARY.relative_to(ROOT))}
    with SUMMARY.open("r", newline="", encoding="utf-8") as stream:
        methods = list(csv.DictReader(stream))
    return {"methods": methods, "source": str(SUMMARY.relative_to(ROOT)),
            "note": "Historical five-seed final test means; not current live IDS performance"}


# Serve the Vite production build from the same read-only localhost API origin.
# The route/mount are intentionally last so /health and /api remain authoritative.
DIST = ROOT / "frontend" / "dist"
if (DIST / "index.html").is_file():
    @app.get("/", include_in_schema=False)
    def dashboard_home():
        return FileResponse(DIST / "index.html")

    app.mount("/assets", StaticFiles(directory=DIST / "assets"), name="dashboard_assets")

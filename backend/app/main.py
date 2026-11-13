from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="EvoNIDS API", version="0.3.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok", "phase": 2}


@app.get("/api/project")
def project():
    return {
        "title": "Multi-Objective Evolutionary Feature Selection for Efficient Network Intrusion Detection",
        "algorithms": ["GA", "BPSO", "PSO", "NSGA-II"],
        "classifiers": ["Logistic Regression", "Random Forest", "XGBoost"],
        "default_repeated_runs": 5,
        "status": "Phase 2: UNSW-NB15 validation and baselines",
    }


@app.get("/api/data/status")
def data_status():
    raw = Path("data/raw")
    train = raw / "UNSW_NB15_training-set.csv"
    test = raw / "UNSW_NB15_testing-set.csv"
    return {
        "train_expected": str(train),
        "test_expected": str(test),
        "train_present": train.exists(),
        "test_present": test.exists(),
        "ready_for_baselines": train.exists() and test.exists(),
    }

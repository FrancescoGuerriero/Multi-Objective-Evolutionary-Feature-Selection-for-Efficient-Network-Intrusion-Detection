from pathlib import Path
import pandas as pd
from prototype.model_io import load_pipeline

def score_csv(csv_path, model_path):
    source = Path(csv_path)
    if not source.is_file():
        raise FileNotFoundError(f"CSV not found: {source}")
    frame = pd.read_csv(source)
    model = load_pipeline(model_path)
    names = getattr(model, "feature_names_in_", None)
    if names is None:
        raise ValueError("A fitted model with named input features is required")
    required = list(names)
    missing = [name for name in required if name not in frame.columns]
    if missing:
        raise ValueError(f"Incompatible flow CSV, missing features: {missing}")
    data = frame[required]
    result = frame.copy()
    result["ids_prediction"] = model.predict(data)
    if hasattr(model, "predict_proba") and 1 in model.classes_:
        result["attack_probability"] = model.predict_proba(data)[:, list(model.classes_).index(1)]
    return result

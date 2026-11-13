from __future__ import annotations

from pathlib import Path

import pandas as pd

from prototype.model_io import load_pipeline


def score_csv(csv_path: str | Path, model_path: str | Path) -> pd.DataFrame:
    csv_path = Path(csv_path)
    if not csv_path.exists():
        raise FileNotFoundError(f"CSV file not found: {csv_path}")

    frame = pd.read_csv(csv_path)
    model = load_pipeline(model_path)

    if hasattr(model, "feature_names_in_"):
        required = list(model.feature_names_in_)
        missing = [name for name in required if name not in frame.columns]
        if missing:
            raise ValueError(f"Input CSV is missing model features: {missing}")
        X = frame[required]
    else:
        X = frame

    predictions = model.predict(X)
    output = frame.copy()
    output["ids_prediction"] = predictions

    if hasattr(model, "predict_proba"):
        probabilities = model.predict_proba(X)
        if getattr(probabilities, "ndim", 1) == 2 and probabilities.shape[1] >= 2:
            output["attack_probability"] = probabilities[:, 1]

    return output

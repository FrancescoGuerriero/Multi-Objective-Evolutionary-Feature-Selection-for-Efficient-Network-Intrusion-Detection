from __future__ import annotations

import argparse
import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="models/demo_pipeline.joblib")
    parser.add_argument("--csv-output", default="results/demo_rows.csv")
    args = parser.parse_args()

    config_path = Path(__file__).parent / "config" / "selected_features.json"
    features = json.loads(config_path.read_text(encoding="utf-8"))["features"]
    categorical = ["service"]
    numerical = [f for f in features if f not in categorical]

    rng = np.random.default_rng(42)
    n = 300
    frame = pd.DataFrame({name: rng.normal(size=n) for name in numerical})
    frame["service"] = rng.choice(["http", "dns", "ssh", "other"], size=n)
    signal = frame["sbytes"] + 0.7 * frame["ct_srv_dst"] - 0.4 * frame["dbytes"]
    y = (signal > np.median(signal)).astype(int)

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", StandardScaler(), numerical),
            ("cat", OneHotEncoder(handle_unknown="ignore"), categorical),
        ]
    )
    pipeline = Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("model", RandomForestClassifier(n_estimators=40, random_state=42, n_jobs=1)),
        ]
    )
    pipeline.fit(frame[features], y)

    target = Path(args.output)
    target.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(pipeline, target)

    demo_rows = frame.head(20).copy()
    csv_target = Path(args.csv_output)
    csv_target.parent.mkdir(parents=True, exist_ok=True)
    demo_rows.to_csv(csv_target, index=False)

    print(f"Created synthetic smoke-test model: {target}")
    print(f"Created synthetic smoke-test rows: {csv_target}")
    print("These synthetic outputs are not coursework benchmark results.")


if __name__ == "__main__":
    main()

"""Synthetic smoke-test training; NOT the reported coursework model."""
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

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--output", default="models/demo_pipeline.joblib")
    p.add_argument("--csv-output", default="results/demo_rows.csv")
    args = p.parse_args()
    features = json.loads((Path(__file__).parent / "config/selected_features.json").read_text())["features"]
    nums = [x for x in features if x != "service"]
    rng = np.random.default_rng(42)
    frame = pd.DataFrame({name: rng.normal(size=300) for name in nums})
    frame["service"] = rng.choice(["http", "dns", "ssh", "other"], size=300)
    signal = frame["sbytes"] + .7*frame["ct_srv_dst"] - .4*frame["dbytes"]
    target = (signal > np.median(signal)).astype(int)
    prep = ColumnTransformer([
        ("num", StandardScaler(), nums),
        ("cat", OneHotEncoder(handle_unknown="ignore"), ["service"])
    ])
    model = Pipeline([("preprocessor", prep),
                      ("model", RandomForestClassifier(n_estimators=40, random_state=42, n_jobs=1))])
    model.fit(frame[features], target)
    out = Path(args.output); out.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, out)
    csv = Path(args.csv_output); csv.parent.mkdir(parents=True, exist_ok=True)
    frame.head(20).to_csv(csv, index=False)
    print(f"Synthetic model: {out}; synthetic rows: {csv}; NOT benchmark evidence")

if __name__ == "__main__":
    main()

"""Near-real-time classification of externally exported compatible flow CSV rows.

Not a Windows packet-capture implementation. It does not construct UNSW-NB15
features from local socket metadata. Exporter appends complete newline rows.
"""
from __future__ import annotations
import csv
import json
import time
from pathlib import Path
import pandas as pd
from prototype.model_io import load_pipeline

def expected_features(model):
    names = getattr(model, "feature_names_in_", None)
    if names is None and hasattr(model, "named_steps"):
        for step in model.named_steps.values():
            names = getattr(step, "feature_names_in_", None)
            if names is not None:
                break
    if names is None:
        raise ValueError("Model must expose feature_names_in_; fit/export a named-column pipeline")
    return [str(x) for x in names]

def classify_rows(frame, model, threshold=.5):
    if not 0 <= threshold <= 1:
        raise ValueError("Threshold must be in [0,1]")
    needed = expected_features(model)
    missing = sorted(set(needed)-set(frame.columns))
    if missing:
        raise ValueError(f"Incompatible flow schema; missing: {missing}")
    result = frame.copy()
    if result.empty:
        return result
    if hasattr(model, "predict_proba"):
        classes = list(getattr(model, "classes_", [0, 1]))
        if 1 not in classes:
            raise ValueError("Attack class 1 is required")
        prob = model.predict_proba(frame[needed])[:, classes.index(1)]
        result["attack_probability"] = prob
        result["ids_prediction"] = (prob >= threshold).astype(int)
    else:
        result["ids_prediction"] = model.predict(frame[needed]).astype(int)
    return result

def read_new_records(path, offset):
    path = Path(path)
    if not path.exists():
        return pd.DataFrame(), 0
    with path.open("r", encoding="utf-8-sig", newline="") as fd:
        header = fd.readline()
        if not header.endswith("\n"):
            return pd.DataFrame(), 0
        names = next(csv.reader([header]))
        if not names or len(names) != len(set(names)):
            raise ValueError("Invalid CSV header")
        start = fd.tell()
        size = path.stat().st_size
        if offset < start or offset > size:
            offset = start
        fd.seek(offset)
        new = fd.read()
        last = new.rfind("\n")
        if last < 0:
            return pd.DataFrame(columns=names), offset
        text = new[:last+1]
        rows = list(csv.reader(text.splitlines()))
        if any(len(row) != len(names) for row in rows):
            raise ValueError("Malformed appended flow CSV row")
        return pd.DataFrame(rows, columns=names), offset+len(text.encode("utf-8"))

def monitor_compatible_flows(csv_path, model_path, *, interval=1., iterations=None,
                             threshold=.5, output=None, emit=None):
    if interval <= 0 or (iterations is not None and iterations < 1):
        raise ValueError("Positive interval and iterations required")
    model = load_pipeline(model_path)
    emit = emit or (lambda record: print(json.dumps(record, default=str)))
    offset, total, count = 0, 0, 0
    target = Path(output) if output else None
    if target:
        target.parent.mkdir(parents=True, exist_ok=True)
    while iterations is None or count < iterations:
        new, offset = read_new_records(csv_path, offset)
        if not new.empty:
            for col in expected_features(model):
                if col in new.columns and col not in {"proto", "service", "state"}:
                    new[col] = pd.to_numeric(new[col], errors="raise")
            scored = classify_rows(new, model, threshold)
            for row in scored.to_dict("records"):
                event = {
                    "source": "compatible_flow_csv",
                    "prediction": int(row["ids_prediction"]),
                    "attack_probability": row.get("attack_probability"),
                    "record": {k:v for k,v in row.items() if k not in {"ids_prediction","attack_probability"}}
                }
                emit(event)
                if target:
                    with target.open("a", encoding="utf-8") as fd:
                        fd.write(json.dumps(event, default=str)+"\n")
                total += 1
        count += 1
        if iterations is None or count < iterations:
            time.sleep(interval)
    return total

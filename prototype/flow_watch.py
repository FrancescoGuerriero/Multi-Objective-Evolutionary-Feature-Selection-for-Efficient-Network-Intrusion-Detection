"""Opt-in live scoring of an externally populated, schema-compatible flow CSV.

This module NEVER generates UNSW-NB15 fields from Windows socket metadata.
The external exporter must provide the trained pipeline's input columns.
"""
from __future__ import annotations

import csv
import json
import time
from pathlib import Path
from typing import Callable

import pandas as pd

from prototype.model_io import load_pipeline


def expected_features(model: object) -> list[str]:
    names = getattr(model, "feature_names_in_", None)
    if names is not None:
        return [str(name) for name in names]
    # sklearn Pipeline often exposes feature_names_in_ from the first step.
    if hasattr(model, "named_steps"):
        for step in model.named_steps.values():
            names = getattr(step, "feature_names_in_", None)
            if names is not None:
                return [str(name) for name in names]
    raise ValueError("Model lacks input feature names; export a fitted named-column Pipeline.")


def classify_rows(frame: pd.DataFrame, model: object, threshold: float = 0.5) -> pd.DataFrame:
    if not 0 <= threshold <= 1:
        raise ValueError("threshold must be between 0 and 1")
    required = expected_features(model)
    missing = sorted(set(required) - set(frame.columns))
    if missing:
        raise ValueError(f"Incompatible flow schema; missing: {missing}")
    if frame.empty:
        return frame.assign(ids_prediction=pd.Series(dtype=int), attack_probability=pd.Series(dtype=float))
    input_rows = frame.loc[:, required]
    result = frame.copy()
    if hasattr(model, "predict_proba"):
        classes = list(getattr(model, "classes_", [0, 1]))
        if 1 not in classes:
            raise ValueError("Binary classifier must expose attack class 1")
        prob = model.predict_proba(input_rows)[:, classes.index(1)]
        result["attack_probability"] = prob
        result["ids_prediction"] = (prob >= threshold).astype(int)
    else:
        result["ids_prediction"] = model.predict(input_rows).astype(int)
    return result


def read_new_records(csv_path: str | Path, offset: int) -> tuple[pd.DataFrame, int]:
    """Read only complete new CSV records, restarting if source is truncated.

    Exporter contract: append complete newline-terminated rows, never change headers.
    """
    path = Path(csv_path)
    if not path.exists():
        return pd.DataFrame(), 0
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        header = handle.readline()
        if not header.endswith("\n"):
            return pd.DataFrame(), 0
        fields = next(csv.reader([header]))
        if not fields or len(fields) != len(set(fields)):
            raise ValueError("Invalid/duplicate CSV header")
        content_start = handle.tell()
        file_size = path.stat().st_size
        if offset < content_start or offset > file_size:
            offset = content_start
        handle.seek(offset)
        text = handle.read()
        last_newline = text.rfind("\n")
        if last_newline == -1:
            return pd.DataFrame(columns=fields), offset
        complete = text[:last_newline + 1]
        # CSV exporter contract excludes embedded newlines in quoted fields.
        lines = complete.splitlines()
        rows = list(csv.reader(lines))
        if any(len(row) != len(fields) for row in rows):
            raise ValueError("Malformed appended flow CSV record")
        new_offset = offset + len(complete.encode("utf-8"))
        return pd.DataFrame(rows, columns=fields), new_offset


def monitor_compatible_flows(
    csv_path: str | Path,
    model_path: str | Path,
    *,
    interval: float = 1.0,
    iterations: int | None = None,
    threshold: float = 0.5,
    output: str | Path | None = None,
    emit: Callable[[dict], None] | None = None,
) -> int:
    """Poll an external compatible CSV and emit predictions, optionally JSONL.

    Returns the number of scored flows. No socket capture or firewall changes.
    """
    if interval <= 0 or (iterations is not None and iterations < 1):
        raise ValueError("interval must be >0 and iterations must be >=1")
    model = load_pipeline(model_path)
    emit = emit or (lambda record: print(json.dumps(record, default=str)))
    offset = 0
    scored_count = 0
    iteration = 0
    destination = Path(output) if output else None
    if destination:
        destination.parent.mkdir(parents=True, exist_ok=True)
    while iterations is None or iteration < iterations:
        new, offset = read_new_records(csv_path, offset)
        if not new.empty:
            # Convert numeric columns from CSV strings while retaining categoricals.
            expected = expected_features(model)
            for col in expected:
                if col in new and col not in {"proto", "service", "state"}:
                    new[col] = pd.to_numeric(new[col], errors="raise")
            scored = classify_rows(new, model, threshold)
            for row in scored.to_dict("records"):
                event = {"source": "compatible_flow_csv", "prediction": int(row["ids_prediction"]),
                         "attack_probability": row.get("attack_probability"),
                         "record": {key: value for key, value in row.items() if key not in {"ids_prediction", "attack_probability"}}}
                emit(event)
                if destination:
                    with destination.open("a", encoding="utf-8") as stream:
                        stream.write(json.dumps(event, default=str) + "\n")
                scored_count += 1
        iteration += 1
        if iterations is None or iteration < iterations:
            time.sleep(interval)
    return scored_count

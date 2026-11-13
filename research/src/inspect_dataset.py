from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd


def inspect_csv(path: Path) -> dict:
    if not path.exists():
        raise FileNotFoundError(path)

    df = pd.read_csv(path)
    categorical = df.select_dtypes(exclude=["number", "bool"]).columns.tolist()
    numeric = df.select_dtypes(include=["number", "bool"]).columns.tolist()

    summary = {
        "path": str(path),
        "rows": int(len(df)),
        "columns": int(df.shape[1]),
        "column_names": df.columns.tolist(),
        "numeric_columns": numeric,
        "categorical_columns": categorical,
        "missing_values_total": int(df.isna().sum().sum()),
        "duplicate_rows": int(df.duplicated().sum()),
    }

    for candidate in ["label", "attack_cat"]:
        if candidate in df.columns:
            counts = df[candidate].value_counts(dropna=False)
            summary[f"{candidate}_distribution"] = {
                str(k): int(v) for k, v in counts.items()
            }

    return summary


def main():
    parser = argparse.ArgumentParser(
        description="Inspect UNSW-NB15 CSV schema and class distributions."
    )
    parser.add_argument("--train", required=True)
    parser.add_argument("--test", required=False)
    parser.add_argument(
        "--output",
        default="results/unsw_schema_report.json",
    )
    args = parser.parse_args()

    payload = {"train": inspect_csv(Path(args.train))}
    if args.test:
        payload["test"] = inspect_csv(Path(args.test))

        train_cols = payload["train"]["column_names"]
        test_cols = payload["test"]["column_names"]
        payload["schema_match"] = train_cols == test_cols

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    print(json.dumps(payload, indent=2))
    print(f"\nSaved schema report: {output}")


if __name__ == "__main__":
    main()

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

from research.src.run_unsw_baseline import DEFAULT_SEEDS, run_once, summarise


DEFAULT_MODELS = ["logistic_regression", "random_forest", "xgboost"]


def _summary_row(model: str, payload: dict) -> dict:
    test = payload["summary"]["test"]
    runtime = payload["summary"]

    row = {
        "model": model,
        "runs": len(payload["runs"]),
        "macro_f1_mean": test["macro_f1"]["mean"],
        "macro_f1_std": test["macro_f1"]["std"],
        "macro_recall_mean": test["macro_recall"]["mean"],
        "macro_recall_std": test["macro_recall"]["std"],
        "balanced_accuracy_mean": test["balanced_accuracy"]["mean"],
        "balanced_accuracy_std": test["balanced_accuracy"]["std"],
        "accuracy_mean": test["accuracy"]["mean"],
        "accuracy_std": test["accuracy"]["std"],
        "training_seconds_mean": runtime["training_seconds"]["mean"],
        "training_seconds_std": runtime["training_seconds"]["std"],
        "inference_ms_per_sample_mean": runtime[
            "test_inference_ms_per_sample"
        ]["mean"],
        "inference_ms_per_sample_std": runtime[
            "test_inference_ms_per_sample"
        ]["std"],
    }

    fpr = test.get("false_positive_rate")
    if fpr is not None:
        row["false_positive_rate_mean"] = fpr["mean"]
        row["false_positive_rate_std"] = fpr["std"]

    return row


def _write_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = []
    for row in rows:
        for key in row:
            if key not in fieldnames:
                fieldnames.append(key)

    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Run all full-feature UNSW-NB15 ML baselines under one controlled "
            "experimental protocol."
        )
    )
    parser.add_argument("--train", required=True)
    parser.add_argument("--test", required=True)
    parser.add_argument(
        "--target",
        choices=["label", "attack_cat"],
        default="label",
    )
    parser.add_argument(
        "--models",
        nargs="+",
        choices=DEFAULT_MODELS,
        default=DEFAULT_MODELS,
    )
    parser.add_argument("--seeds", nargs="*", type=int, default=DEFAULT_SEEDS)
    parser.add_argument(
        "--output-dir",
        default="results/baselines",
    )
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    suite = {
        "protocol": (
            "UNSW-NB15 official test partition; validation split from training "
            "only; identical seeds and preprocessing policy per model"
        ),
        "target": args.target,
        "seeds": args.seeds,
        "models": {},
    }
    summary_rows: list[dict] = []

    for model in args.models:
        print(f"\n=== {model} ===")
        runs = []
        for seed in args.seeds:
            print(f"seed={seed}")
            result = run_once(
                args.train,
                args.test,
                args.target,
                model,
                seed,
            )
            runs.append(result)
            print(
                "  test macro-F1="
                f"{result['test_metrics']['macro_f1']:.6f}, "
                "balanced accuracy="
                f"{result['test_metrics']['balanced_accuracy']:.6f}"
            )

        model_payload = {
            "model": model,
            "runs": runs,
            "summary": summarise(runs),
        }
        suite["models"][model] = model_payload

        model_json = output_dir / f"{args.target}_{model}.json"
        model_json.write_text(
            json.dumps(model_payload, indent=2),
            encoding="utf-8",
        )
        summary_rows.append(_summary_row(model, model_payload))

    suite_path = output_dir / f"{args.target}_baseline_suite.json"
    suite_path.write_text(json.dumps(suite, indent=2), encoding="utf-8")

    csv_path = output_dir / f"{args.target}_baseline_summary.csv"
    _write_csv(csv_path, summary_rows)

    print("\nBaseline suite complete")
    print(f"JSON: {suite_path}")
    print(f"CSV:  {csv_path}")


if __name__ == "__main__":
    main()

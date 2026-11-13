from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import numpy as np
from sklearn.pipeline import Pipeline

from research.src.models.factory import create_model
from research.src.models.metrics import classification_metrics
from research.src.models.preprocessing import build_preprocessor
from research.src.utils.data import load_unsw_official_split
from research.src.utils.seed import set_global_seed


DEFAULT_SEEDS = [42, 101, 202, 303, 404]


def run_once(
    train_csv: str,
    test_csv: str,
    target: str,
    model_name: str,
    seed: int,
) -> dict:
    set_global_seed(seed)

    split = load_unsw_official_split(
        train_csv,
        test_csv,
        target_column=target,
        seed=seed,
        validation_size=0.20,
    )

    pipeline = Pipeline(
        steps=[
            ("preprocessor", build_preprocessor(split.X_train)),
            ("model", create_model(model_name, seed=seed)),
        ]
    )

    train_start = time.perf_counter()
    pipeline.fit(split.X_train, split.y_train)
    training_seconds = time.perf_counter() - train_start

    valid_start = time.perf_counter()
    valid_predictions = pipeline.predict(split.X_valid)
    validation_seconds = time.perf_counter() - valid_start

    test_start = time.perf_counter()
    test_predictions = pipeline.predict(split.X_test)
    inference_seconds = time.perf_counter() - test_start

    validation_metrics = classification_metrics(split.y_valid, valid_predictions)
    test_metrics = classification_metrics(split.y_test, test_predictions)

    return {
        "seed": seed,
        "model": model_name,
        "target": target,
        "n_model_features_before_encoding": int(split.X_train.shape[1]),
        "n_train": int(len(split.X_train)),
        "n_valid": int(len(split.X_valid)),
        "n_test": int(len(split.X_test)),
        "training_seconds": float(training_seconds),
        "validation_seconds": float(validation_seconds),
        "test_inference_seconds": float(inference_seconds),
        "test_inference_ms_per_sample": float(
            (inference_seconds / max(len(split.X_test), 1)) * 1000.0
        ),
        "validation_metrics": validation_metrics,
        "test_metrics": test_metrics,
    }


def summarise(runs: list[dict]) -> dict:
    metric_names = [
        "accuracy",
        "balanced_accuracy",
        "macro_precision",
        "macro_recall",
        "macro_f1",
        "weighted_f1",
        "false_positive_rate",
    ]
    result = {"validation": {}, "test": {}}

    for section, source_key in [
        ("validation", "validation_metrics"),
        ("test", "test_metrics"),
    ]:
        for metric in metric_names:
            raw_values = [run[source_key].get(metric) for run in runs]
            values_present = [value for value in raw_values if value is not None]
            if not values_present:
                result[section][metric] = None
                continue
            values = np.array(values_present, dtype=float)
            result[section][metric] = {
                "mean": float(values.mean()),
                "std": float(values.std(ddof=1)) if len(values) > 1 else 0.0,
            }

    for metric in [
        "training_seconds",
        "test_inference_seconds",
        "test_inference_ms_per_sample",
    ]:
        values = np.array([run[metric] for run in runs], dtype=float)
        result[metric] = {
            "mean": float(values.mean()),
            "std": float(values.std(ddof=1)) if len(values) > 1 else 0.0,
        }

    return result


def main():
    parser = argparse.ArgumentParser(
        description="Run repeated UNSW-NB15 baselines using the official test partition."
    )
    parser.add_argument("--train", required=True)
    parser.add_argument("--test", required=True)
    parser.add_argument(
        "--target",
        choices=["label", "attack_cat"],
        default="label",
        help="label=binary IDS; attack_cat=multiclass attack classification",
    )
    parser.add_argument(
        "--model",
        choices=["logistic_regression", "random_forest", "xgboost"],
        default="random_forest",
    )
    parser.add_argument("--seeds", nargs="*", type=int, default=DEFAULT_SEEDS)
    parser.add_argument(
        "--output",
        default=None,
        help="Defaults to results/baseline_<target>_<model>.json",
    )
    args = parser.parse_args()

    runs = [
        run_once(
            args.train,
            args.test,
            args.target,
            args.model,
            seed,
        )
        for seed in args.seeds
    ]

    payload = {
        "protocol": "UNSW-NB15 official test partition; validation split from training only",
        "target": args.target,
        "model": args.model,
        "seeds": args.seeds,
        "runs": runs,
        "summary": summarise(runs),
    }

    output = Path(
        args.output
        or f"results/baseline_{args.target}_{args.model}.json"
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    print(json.dumps(payload["summary"], indent=2))
    print(f"\nSaved: {output}")


if __name__ == "__main__":
    main()

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import pandas as pd
from sklearn.model_selection import train_test_split


@dataclass(frozen=True)
class DatasetSplit:
    X_train: pd.DataFrame
    X_valid: pd.DataFrame
    X_test: pd.DataFrame
    y_train: pd.Series
    y_valid: pd.Series
    y_test: pd.Series


def load_csv_dataset(
    csv_path: str | Path,
    target_column: str,
    drop_columns: Iterable[str] | None = None,
) -> tuple[pd.DataFrame, pd.Series]:
    path = Path(csv_path)
    if not path.exists():
        raise FileNotFoundError(
            f"Dataset not found: {path}. Put the dataset under data/raw/ "
            "or provide an explicit CSV path."
        )

    df = pd.read_csv(path)

    if target_column not in df.columns:
        raise ValueError(
            f"Target column '{target_column}' not found. "
            f"Available columns: {list(df.columns)}"
        )

    if drop_columns:
        to_drop = [c for c in drop_columns if c in df.columns and c != target_column]
        df = df.drop(columns=to_drop)

    y = df[target_column].copy()
    X = df.drop(columns=[target_column]).copy()
    return X, y


def make_train_valid_test_split(
    X: pd.DataFrame,
    y: pd.Series,
    seed: int,
    test_size: float = 0.20,
    validation_size: float = 0.20,
) -> DatasetSplit:
    """Generic split helper for datasets without an official held-out test set."""
    stratify = y if y.nunique() > 1 else None

    X_train_valid, X_test, y_train_valid, y_test = train_test_split(
        X,
        y,
        test_size=test_size,
        random_state=seed,
        stratify=stratify,
    )

    relative_valid = validation_size / (1.0 - test_size)
    stratify_tv = y_train_valid if y_train_valid.nunique() > 1 else None

    X_train, X_valid, y_train, y_valid = train_test_split(
        X_train_valid,
        y_train_valid,
        test_size=relative_valid,
        random_state=seed,
        stratify=stratify_tv,
    )

    return DatasetSplit(
        X_train=X_train,
        X_valid=X_valid,
        X_test=X_test,
        y_train=y_train,
        y_valid=y_valid,
        y_test=y_test,
    )


def _unsw_drop_columns(target_column: str) -> list[str]:
    """Prevent obvious target leakage for the common UNSW-NB15 train/test CSVs."""
    target = target_column.lower()
    drops = ["id"]

    if target == "label":
        # attack_cat directly encodes the attack/normal outcome and would leak the binary target.
        drops.append("attack_cat")
    elif target == "attack_cat":
        # label is a binary representation of attack-vs-normal and would leak information.
        drops.append("label")

    return drops


def load_unsw_official_split(
    train_csv: str | Path,
    test_csv: str | Path,
    *,
    target_column: str = "label",
    seed: int = 42,
    validation_size: float = 0.20,
) -> DatasetSplit:
    """Load UNSW-NB15's published train/test partitions.

    The official test partition remains untouched. A validation subset is
    created only from the published training partition.
    """
    train_path = Path(train_csv)
    test_path = Path(test_csv)

    if not train_path.exists():
        raise FileNotFoundError(f"Training CSV not found: {train_path}")
    if not test_path.exists():
        raise FileNotFoundError(f"Testing CSV not found: {test_path}")

    train_df = pd.read_csv(train_path)
    test_df = pd.read_csv(test_path)

    if target_column not in train_df.columns:
        raise ValueError(f"Target '{target_column}' missing from training CSV.")
    if target_column not in test_df.columns:
        raise ValueError(f"Target '{target_column}' missing from testing CSV.")

    # The two official partition files should expose the same columns.
    if set(train_df.columns) != set(test_df.columns):
        missing_train = sorted(set(test_df.columns) - set(train_df.columns))
        missing_test = sorted(set(train_df.columns) - set(test_df.columns))
        raise ValueError(
            "Training/testing schemas differ. "
            f"Missing from train={missing_train}, missing from test={missing_test}"
        )

    drops = [c for c in _unsw_drop_columns(target_column) if c in train_df.columns]

    y_train_full = train_df[target_column].copy()
    X_train_full = train_df.drop(columns=[target_column, *drops]).copy()

    y_test = test_df[target_column].copy()
    X_test = test_df.drop(columns=[target_column, *drops]).copy()

    stratify = y_train_full if y_train_full.nunique() > 1 else None
    X_train, X_valid, y_train, y_valid = train_test_split(
        X_train_full,
        y_train_full,
        test_size=validation_size,
        random_state=seed,
        stratify=stratify,
    )

    return DatasetSplit(
        X_train=X_train.reset_index(drop=True),
        X_valid=X_valid.reset_index(drop=True),
        X_test=X_test.reset_index(drop=True),
        y_train=y_train.reset_index(drop=True),
        y_valid=y_valid.reset_index(drop=True),
        y_test=y_test.reset_index(drop=True),
    )

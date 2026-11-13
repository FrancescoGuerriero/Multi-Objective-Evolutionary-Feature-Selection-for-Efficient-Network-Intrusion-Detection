from __future__ import annotations

from typing import Any

import numpy as np
from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    confusion_matrix,
    precision_recall_fscore_support,
)


def _binary_false_positive_rate(y_true, y_pred) -> float | None:
    """Return FP / (FP + TN) for binary classification.

    Returns None for non-binary targets. The positive class is the second class
    in sorted unique-label order, which is appropriate for UNSW-NB15's 0/1
    `label` target.
    """
    labels = np.unique(np.concatenate([np.asarray(y_true), np.asarray(y_pred)]))
    if len(labels) != 2:
        return None

    matrix = confusion_matrix(y_true, y_pred, labels=labels)
    tn, fp, _, _ = matrix.ravel()
    denominator = fp + tn
    return float(fp / denominator) if denominator else 0.0


def classification_metrics(y_true, y_pred) -> dict[str, Any]:
    """Compute the common EvoNIDS classification metrics.

    Macro-F1 is the primary quality metric because it weights classes equally,
    while balanced accuracy and macro recall expose performance hidden by class
    imbalance. Binary false-positive rate is reported for the main intrusion
    detection task.
    """
    macro_p, macro_r, macro_f1, _ = precision_recall_fscore_support(
        y_true,
        y_pred,
        average="macro",
        zero_division=0,
    )
    weighted_p, weighted_r, weighted_f1, _ = precision_recall_fscore_support(
        y_true,
        y_pred,
        average="weighted",
        zero_division=0,
    )

    labels = np.unique(np.concatenate([np.asarray(y_true), np.asarray(y_pred)]))
    matrix = confusion_matrix(y_true, y_pred, labels=labels)

    return {
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "balanced_accuracy": float(balanced_accuracy_score(y_true, y_pred)),
        "macro_precision": float(macro_p),
        "macro_recall": float(macro_r),
        "macro_f1": float(macro_f1),
        "weighted_precision": float(weighted_p),
        "weighted_recall": float(weighted_r),
        "weighted_f1": float(weighted_f1),
        "false_positive_rate": _binary_false_positive_rate(y_true, y_pred),
        "labels": [str(label) for label in labels.tolist()],
        "confusion_matrix": matrix.tolist(),
    }

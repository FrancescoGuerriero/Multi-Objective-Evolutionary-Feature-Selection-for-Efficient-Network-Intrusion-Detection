import pytest

from research.src.models.metrics import classification_metrics


def test_classification_metrics_contains_macro_f1():
    result = classification_metrics([0, 0, 1, 1], [0, 1, 1, 1])
    assert "macro_f1" in result
    assert 0.0 <= result["macro_f1"] <= 1.0


def test_binary_false_positive_rate():
    # TN=1, FP=1, FN=0, TP=2 => FPR = 1 / (1 + 1) = 0.5
    result = classification_metrics([0, 0, 1, 1], [0, 1, 1, 1])
    assert result["false_positive_rate"] == pytest.approx(0.5)


def test_multiclass_false_positive_rate_is_not_reported():
    result = classification_metrics([0, 1, 2], [0, 2, 1])
    assert result["false_positive_rate"] is None

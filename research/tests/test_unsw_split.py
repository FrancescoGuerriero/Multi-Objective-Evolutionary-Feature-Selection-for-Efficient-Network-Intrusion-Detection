import pandas as pd

from research.src.utils.data import load_unsw_official_split


def test_unsw_binary_target_removes_attack_category_and_id(tmp_path):
    train = pd.DataFrame(
        {
            "id": range(20),
            "dur": range(20),
            "proto": ["tcp", "udp"] * 10,
            "attack_cat": ["Normal", "Generic"] * 10,
            "label": [0, 1] * 10,
        }
    )
    test = pd.DataFrame(
        {
            "id": range(8),
            "dur": range(8),
            "proto": ["tcp", "udp"] * 4,
            "attack_cat": ["Normal", "Generic"] * 4,
            "label": [0, 1] * 4,
        }
    )
    train_path = tmp_path / "train.csv"
    test_path = tmp_path / "test.csv"
    train.to_csv(train_path, index=False)
    test.to_csv(test_path, index=False)

    split = load_unsw_official_split(
        train_path,
        test_path,
        target_column="label",
        seed=42,
    )

    assert "label" not in split.X_train.columns
    assert "attack_cat" not in split.X_train.columns
    assert "id" not in split.X_train.columns
    assert len(split.X_test) == 8


def test_unsw_multiclass_target_removes_binary_label(tmp_path):
    train = pd.DataFrame(
        {
            "id": range(20),
            "dur": range(20),
            "attack_cat": ["Normal", "Generic"] * 10,
            "label": [0, 1] * 10,
        }
    )
    test = pd.DataFrame(
        {
            "id": range(8),
            "dur": range(8),
            "attack_cat": ["Normal", "Generic"] * 4,
            "label": [0, 1] * 4,
        }
    )
    train_path = tmp_path / "train.csv"
    test_path = tmp_path / "test.csv"
    train.to_csv(train_path, index=False)
    test.to_csv(test_path, index=False)

    split = load_unsw_official_split(
        train_path,
        test_path,
        target_column="attack_cat",
        seed=42,
    )

    assert "attack_cat" not in split.X_train.columns
    assert "label" not in split.X_train.columns
    assert "id" not in split.X_train.columns

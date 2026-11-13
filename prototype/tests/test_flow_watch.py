from __future__ import annotations
import json
import pandas as pd
import numpy as np
import pytest
from prototype.flow_watch import classify_rows, read_new_records, monitor_compatible_flows


class FakeModel:
    feature_names_in_ = np.array(["sbytes", "service"], dtype=object)
    classes_ = np.array([0, 1])
    def predict_proba(self, frame):
        p = np.where(frame["sbytes"].astype(float) > 10, .9, .1)
        return np.c_[1-p, p]


def test_classify_rejects_incompatible_columns():
    with pytest.raises(ValueError, match="missing"):
        classify_rows(pd.DataFrame({"sbytes": [1]}), FakeModel())


def test_classify_threshold():
    result = classify_rows(pd.DataFrame({"sbytes": [2, 20], "service": ["dns", "http"]}), FakeModel())
    assert result["ids_prediction"].tolist() == [0, 1]


def test_new_rows_only_and_partial_line(tmp_path):
    path = tmp_path / "incoming.csv"
    path.write_text("sbytes,service\n2,dns\n20,htt", encoding="utf-8")
    first, offset = read_new_records(path, 0)
    assert first["service"].tolist() == ["dns"]
    with path.open("a", encoding="utf-8") as out:
        out.write("p\n")
    second, offset2 = read_new_records(path, offset)
    assert second["service"].tolist() == ["http"]
    third, _ = read_new_records(path, offset2)
    assert third.empty


def test_polling_emits_once(tmp_path, monkeypatch):
    path = tmp_path / "flows.csv"
    path.write_text("sbytes,service\n20,http\n", encoding="utf-8")
    monkeypatch.setattr("prototype.flow_watch.load_pipeline", lambda _: FakeModel())
    events = []
    count = monitor_compatible_flows(path, "fake.joblib", interval=.001, iterations=2, emit=events.append)
    assert count == 1
    assert events[0]["prediction"] == 1
    assert events[0]["source"] == "compatible_flow_csv"

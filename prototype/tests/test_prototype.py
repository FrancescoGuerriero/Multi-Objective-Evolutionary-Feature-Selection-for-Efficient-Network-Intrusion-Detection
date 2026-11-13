from __future__ import annotations

import json
from pathlib import Path

from prototype.telemetry import snapshot_connections


def test_selected_feature_config_exists() -> None:
    path = Path("prototype/config/selected_features.json")
    data = json.loads(path.read_text(encoding="utf-8"))
    assert len(data["features"]) == 10
    assert "service" in data["features"]


def test_passive_connection_snapshot_returns_list() -> None:
    assert isinstance(snapshot_connections(), list)

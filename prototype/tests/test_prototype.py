import json
from pathlib import Path
from prototype.telemetry import snapshot_connections

def test_feature_config_is_demo_only():
    file = Path(__file__).resolve().parents[1] / "config" / "selected_features.json"
    data = json.loads(file.read_text(encoding="utf-8"))
    assert len(data["features"]) == 10
    assert "NOT the final" in data["purpose"]

def test_socket_snapshot():
    assert isinstance(snapshot_connections(), list)

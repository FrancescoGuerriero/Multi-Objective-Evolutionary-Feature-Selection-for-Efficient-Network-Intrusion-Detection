from pathlib import Path
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_scope_and_status():
    result = client.get('/api/ids/status')
    assert result.status_code == 200
    assert result.json()['socket_ml_inference'] is False
    assert result.json()['windows_socket_monitor'] == 'passive'

def test_connections():
    result = client.get('/api/ids/connections')
    assert result.status_code == 200
    assert isinstance(result.json()['connections'], list)

def test_research():
    result = client.get('/api/research/comparison')
    assert result.status_code == 200
    assert any(row['method'] == 'GA + RF' for row in result.json()['methods'])

def test_alerts():
    assert client.get('/api/ids/alerts').status_code == 200

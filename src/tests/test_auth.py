import os
import pytest
import requests_mock
from fastapi.testclient import TestClient
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from main import app

client = TestClient(app)

@pytest.fixture
def mock_keycloak_token_request():
    with requests_mock.Mocker() as m:
        url = "https://keycloak.test.aclimate.org/realms/aclimate/protocol/openid-connect/token"
        m.post(url, json={
            "access_token": "fake-access-token",
            "refresh_token": "fake-refresh-token"
        }, status_code=200)
        yield

def test_login_success(monkeypatch, mock_keycloak_token_request):
    # Setea las variables que se usan en routers/auth.py
    monkeypatch.setenv("KEYCLOAK_URL", "https://keycloak.test.aclimate.org")
    monkeypatch.setenv("REALM_NAME", "aclimate")
    monkeypatch.setenv("CLIENT_ID", "dummy-client")
    monkeypatch.setenv("CLIENT_SECRET", "dummy-secret")

    response = client.post("/auth/login", json={
        "username": "demo",
        "password": "demo123"
    })

    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["access_token"] == "fake-access-token"

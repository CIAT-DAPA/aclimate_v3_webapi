import os
import pytest
import respx
from fastapi.testclient import TestClient
from httpx import Response
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from main import app

client = TestClient(app)

@respx.mock
def test_get_client_token_success(monkeypatch):
    monkeypatch.setenv("KEYCLOAK_URL", "https://keycloak.test.aclimate.org")
    monkeypatch.setenv("REALM_NAME", "aclimate")

    token_url = "https://keycloak.test.aclimate.org/realms/aclimate/protocol/openid-connect/token"

    # Mock del endpoint
    respx.post(token_url).mock(
        return_value=Response(200, json={
            "access_token": "fake-token",
            "expires_in": 300
        })
    )

    response = client.post("/auth/get-client-token", json={
        "client_id": "dummy-client",
        "client_secret": "dummy-secret"
    })

    assert response.status_code == 200
    assert response.json()["access_token"] == "fake-token"
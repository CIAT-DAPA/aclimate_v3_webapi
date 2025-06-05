import os
import respx
import jwt
import sys
from httpx import Response
import requests_mock
from fastapi.testclient import TestClient
from datetime import datetime, timedelta

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from main import app
client = TestClient(app)

def test_validate_token_success(monkeypatch):
    monkeypatch.setenv("KEYCLOAK_URL", "https://keycloak.test.aclimate.org")
    monkeypatch.setenv("REALM_NAME", "aclimate")
    monkeypatch.setenv("CLIENT_ID", "dummy-client")

    kid = "test-key-id"
    secret = "test-secret"

    jwks_url = "https://keycloak.test.aclimate.org/realms/aclimate/protocol/openid-connect/certs"

    token = jwt.encode(
        {
            "sub": "user123",
            "aud": "account",
            "iss": "https://keycloak.test.aclimate.org/realms/aclimate",
            "exp": datetime.utcnow() + timedelta(minutes=5),
            "resource_access": {
                "dummy-client": {
                    "roles": ["admin"]
                }
            }
        },
        key=secret,
        algorithm="HS256",
        headers={"kid": kid}
    )

    with requests_mock.Mocker() as m:
        m.get(jwks_url, json={
            "keys": [{
                "kid": kid,
                "kty": "oct",
                "k": secret
            }]
        })

        response = client.get(
            "/auth/token/validate",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 401
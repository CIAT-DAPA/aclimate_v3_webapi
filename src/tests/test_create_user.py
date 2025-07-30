import os
import pytest
import respx
from httpx import Response
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch


import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from dependencies import auth_dependencies
from main import app
client = TestClient(app)

@pytest.fixture
def mock_keycloak_requests():
    with respx.mock:
        respx.post("http://localhost:8080/realms/aclimate/protocol/openid-connect/token").mock(
            return_value=Response(200, json={"access_token": "fake-admin-token"})
        )
        respx.post("http://localhost:8080/admin/realms/aclimate/users").mock(
            return_value=Response(201)
        )
        respx.get("http://localhost:8080/admin/realms/aclimate/users?username=testuser").mock(
            return_value=Response(200, json=[{"id": "fake-user-id"}])
        )
        yield

def override_require_roles_adminsuper():
    return {"username": "adminuser", "roles": ["adminsuper"]}

def test_crear_usuario_success(mock_keycloak_requests):
    app.dependency_overrides[auth_dependencies.require_roles(["adminsuper"])] = override_require_roles_adminsuper

    payload = {
        "username": "testuser",
        "email": "test@example.com",
        "firstName": "Test",
        "lastName": "User",
        "emailVerified": True,
        "enabled": True,
        "credentials": [{"value": "testpassword"}],
        "attributes": {"department": "R&D"}
    }

    response = client.post("/users/crete-user", json=payload)

    assert response.status_code == 404

    app.dependency_overrides = {}

from fastapi.testclient import TestClient
import os
import sys
import pytest
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from main import app
from dependencies.auth_dependencies import get_current_user 

client = TestClient(app)

@pytest.fixture
def mock_countries_data():
    class Country:
        def __init__(self, id, name, iso2):
            self.id = id
            self.name = name
            self.iso2 = iso2

    return [
        Country(id=1, name="Colombia", iso2="CO"),
        Country(id=2, name="Ecuador", iso2="EC")
    ]

def test_get_all_countries(mock_countries_data):
    mock_user = {
        "sub": "user123",
        "preferred_username": "mockuser",
        "resource_access": {
            "dummy-client": {
                "roles": ["admin"]
            }
        }
    }

    app.dependency_overrides[get_current_user] = lambda: mock_user

    from unittest.mock import patch
    with patch("aclimate_v3_orm.services.mng_country_service.MngCountryService.get_all_enable", return_value=mock_countries_data):
        response = client.get("/countries")
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 2
        for item in data:
            assert "id" in item
            assert "name" in item
            assert "iso2" in item

    app.dependency_overrides = {}

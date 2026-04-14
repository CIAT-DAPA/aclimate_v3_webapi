from fastapi.testclient import TestClient
import os
import sys
import pytest
from unittest.mock import patch

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from main import app
from dependencies.auth_dependencies import get_current_user

client = TestClient(app)

@pytest.fixture
def mock_admin1_data():
    class Country:
        def __init__(self, id, name, iso2):
            self.id = id
            self.name = name
            self.iso2 = iso2

    class Admin1:
        def __init__(self, id, name, country, ext_id):
            self.id = id
            self.name = name
            self.country = country
            self.ext_id = ext_id

    country1 = Country(id=1, name="Colombia", iso2="CO")
    country2 = Country(id=2, name="Ecuador", iso2="EC")

    return {
        1: [Admin1(id=101, name="Antioquia", country=country1, ext_id="05")],
        2: [Admin1(id=201, name="Pichincha", country=country2, ext_id="17")],
    }

def test_get_admin1_by_country_ids(mock_admin1_data):
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

    with patch("aclimate_v3_orm.services.mng_admin_1_service.MngAdmin1Service.get_by_country_id") as mock_method:
        mock_method.side_effect = lambda cid: mock_admin1_data.get(cid, [])

        response = client.get("/admin1/by-country-ids", params={"country_ids": "1,2"})
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 2

        expected = {
            101: {"name": "Antioquia", "ext_id": "05", "country_id": 1, "country_name": "Colombia", "country_iso2": "CO"},
            201: {"name": "Pichincha", "ext_id": "17", "country_id": 2, "country_name": "Ecuador", "country_iso2": "EC"},
        }

        for item in data:
            assert item["id"] in expected
            expected_item = expected[item["id"]]
            assert item["name"] == expected_item["name"]
            assert item["ext_id"] == expected_item["ext_id"]
            assert item["country_id"] == expected_item["country_id"]
            assert item["country_name"] == expected_item["country_name"]
            assert item["country_iso2"] == expected_item["country_iso2"]

    app.dependency_overrides = {}

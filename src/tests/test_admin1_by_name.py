# test_admin1_by_name.py

from fastapi.testclient import TestClient
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from main import app  
import pytest

from unittest.mock import patch, MagicMock
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

    return [
        Admin1(id=1, name="Antioquia", country=country1, ext_id="05"),
        Admin1(id=2, name="Antisana", country=country2, ext_id="17"),
        Admin1(id=3, name="Bogotá", country=country1, ext_id="11"),
    ]

def test_get_admin1_by_name(mock_admin1_data):
    with patch("aclimate_v3_orm.services.mng_admin_1_service.MngAdmin1Service.get_all", return_value=mock_admin1_data):
        response = client.get("/admin1/by-name", params={"name": "anti"})
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 2

        for item in data:
            assert "id" in item
            assert "name" in item
            assert "ext_id" in item
            assert "country_id" in item
            assert "country_name" in item
            assert "country_iso2" in item
            assert "anti" in item["name"].lower()
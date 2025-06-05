from fastapi.testclient import TestClient
import os
import sys
import pytest
from unittest.mock import patch

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from main import app

client = TestClient(app)

@pytest.fixture
def mock_admin1_data():
    class Country:
        def __init__(self, id, name, iso2):
            self.id = id
            self.name = name
            self.iso2 = iso2

    class Admin1:
        def __init__(self, id, name, country):
            self.id = id
            self.name = name
            self.country = country

    country1 = Country(id=1, name="Colombia", iso2="CO")
    country2 = Country(id=2, name="Ecuador", iso2="EC")

    return {
        1: [Admin1(id=101, name="Antioquia", country=country1)],
        2: [Admin1(id=201, name="Pichincha", country=country2)],
    }

def test_get_admin1_by_country_ids(mock_admin1_data):
    # Simular llamadas secuenciales a get_by_country_id con side_effect
    with patch("aclimate_v3_orm.services.mng_admin_1_service.MngAdmin1Service.get_by_country_id") as mock_method:
        mock_method.side_effect = lambda cid: mock_admin1_data.get(cid, [])
        
        response = client.get("/admin1/by-country-ids", params={"country_ids": "1,2"})
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 2

        expected_ids = {101, 201}
        for item in data:
            assert "id" in item and item["id"] in expected_ids
            assert "name" in item
            assert "country_id" in item
            assert "country_name" in item
            assert "country_iso2" in item

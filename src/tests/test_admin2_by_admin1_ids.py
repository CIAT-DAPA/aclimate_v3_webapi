
from fastapi.testclient import TestClient
import os
import sys
import pytest
from unittest.mock import patch

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from main import app

client = TestClient(app)

@pytest.fixture
def mock_admin2_data():
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

    class Admin2:
        def __init__(self, id, name, admin_1):
            self.id = id
            self.name = name
            self.admin_1 = admin_1

    country = Country(id=1, name="Colombia", iso2="CO")
    admin1 = Admin1(id=10, name="Antioquia", country=country)
    return [
        Admin2(id=100, name="Medellín", admin_1=admin1),
        Admin2(id=101, name="Envigado", admin_1=admin1)
    ]

def test_get_admin2_by_admin1_ids(mock_admin2_data):
    with patch("aclimate_v3_orm.services.mng_admin_2_service.MngAdmin2Service.get_by_admin1_id", return_value=mock_admin2_data):
        response = client.get("/admin2/by-admin1-ids", params={"admin1_ids": "10"})
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 2

        for item in data:
            assert "id" in item
            assert "name" in item
            assert "admin1_id" in item
            assert "admin1_name" in item
            assert "country_id" in item
            assert "country_name" in item
            assert "country_iso2" in item

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
        def __init__(self, id, name, country, ext_id):
            self.id = id
            self.name = name
            self.country = country
            self.ext_id = ext_id

    class Admin2:
        def __init__(self, id, name, admin_1, ext_id):
            self.id = id
            self.name = name
            self.admin_1 = admin_1
            self.ext_id = ext_id

    country = Country(id=1, name="Colombia", iso2="CO")
    admin1 = Admin1(id=101, name="Pacífico", country=country, ext_id="76")
    return [
        Admin2(id=302, name="Valle del Cauca", admin_1=admin1, ext_id="76001"),
        Admin2(id=303, name="Cauca", admin_1=admin1, ext_id="19001")
    ]

def test_get_admin2_by_country_ids(mock_admin2_data):
    with patch("aclimate_v3_orm.services.mng_admin_2_service.MngAdmin2Service.get_by_country_id", return_value=mock_admin2_data):
        response = client.get("/admin2/by-country-ids", params={"country_ids": "1"})
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 2

        for item in data:
            assert "id" in item
            assert "name" in item
            assert "ext_id" in item
            assert "admin1_id" in item
            assert "admin1_name" in item
            assert "admin1_ext_id" in item
            assert "country_id" in item
            assert "country_name" in item
            assert "country_iso2" in item
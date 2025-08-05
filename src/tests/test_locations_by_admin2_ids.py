from fastapi.testclient import TestClient
import pytest
from unittest.mock import patch
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from main import app

client = TestClient(app)

@pytest.fixture
def mock_locations():
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

    class Location:
        def __init__(self, id, name, ext_id, visible, admin_2, altitude=100.0, latitude=3.45, longitude=-76.53):
            self.id = id
            self.name = name
            self.ext_id = ext_id
            self.visible = visible
            self.admin_2 = admin_2
            self.altitude = altitude
            self.latitude = latitude
            self.longitude = longitude
            self.enable = True

    country = Country(1, "Colombia", "CO")
    admin1 = Admin1(10, "Cundinamarca", country)
    admin2 = Admin2(20, "Bogotá", admin1)

    return [
        Location(101, "Test Location", "EXT101", True, admin2, 123.45, 4.5, -74.1)
    ]

def test_get_locations_by_admin2_ids(mock_locations):
    with patch("aclimate_v3_orm.services.mng_location_service.MngLocationService.get_by_admin2_id", return_value=mock_locations):
        response = client.get("/locations/by-admin2-ids", params={"admin2_ids": "20"})

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 1

        loc = data[0]
        assert loc["id"] == 101
        assert loc["name"] == "Test Location"
        assert loc["ext_id"] == "EXT101"
        assert loc["visible"] is True
        assert loc["admin2_id"] == 20
        assert loc["admin2_name"] == "Bogotá"
        assert loc["admin1_id"] == 10
        assert loc["admin1_name"] == "Cundinamarca"
        assert loc["country_id"] == 1
        assert loc["country_name"] == "Colombia"
        assert loc["country_iso2"] == "CO"

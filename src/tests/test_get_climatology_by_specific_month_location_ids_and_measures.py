
import os
import sys
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from main import app

client = TestClient(app)

@pytest.fixture
def mock_climatology_data():
    class Location:
        def __init__(self, name):
            self.name = name

    class Measure:
        def __init__(self, id, name, short_name, unit):
            self.id = id
            self.name = name
            self.short_name = short_name
            self.unit = unit

    class Climatology:
        def __init__(self, id, location_id, location, measure_id, measure, month, value):
            self.id = id
            self.location_id = location_id
            self.location = location
            self.measure_id = measure_id
            self.measure = measure
            self.month = month
            self.value = value

    location = Location("Valle de Test")
    measure1 = Measure(1, "Temperatura Máxima", "tmax", "°C")
    measure2 = Measure(2, "Precipitación", "ppt", "mm")

    return [
        Climatology(1, 10, location, 1, measure1, 5, 32.1),
        Climatology(2, 10, location, 2, measure2, 5, 200.5),
        Climatology(3, 11, location, 1, measure1, 6, 31.4), 
    ]

def test_get_climatology_by_specific_month_location_ids_and_measures(mock_climatology_data):
    with patch(
        "aclimate_v3_orm.services.climate_historical_climatology_service.ClimateHistoricalClimatologyService.get_by_location_id"
    ) as mock_get:
        def side_effect(location_id):
            return [d for d in mock_climatology_data if d.location_id == location_id]
        mock_get.side_effect = side_effect

        response = client.get(
            "/climatology/by-specific-month-location-ids-and-measures",
            params={"location_ids": "10,11", "measures": "tmax,ppt", "month": 5}
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 2  

        for item in data:
            assert item["month"] == 5
            assert item["measure_short_name"] in ["tmax", "ppt"]
            assert "location_id" in item
            assert "measure_id" in item
            assert "value" in item

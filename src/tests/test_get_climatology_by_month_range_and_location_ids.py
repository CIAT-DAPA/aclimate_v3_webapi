# test_get_climatology_by_month_range_and_location_ids.py

import os
import sys
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

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

    location = Location(name="Sample Location")
    measure = Measure(id=4, name="Temperatura Máxima", short_name="tmax", unit="°C")

    return [
        Climatology(id=1, location_id=456, location=location, measure_id=4, measure=measure, month=5, value=32.7),
        Climatology(id=2, location_id=456, location=location, measure_id=4, measure=measure, month=6, value=31.2),
        Climatology(id=3, location_id=789, location=location, measure_id=4, measure=measure, month=4, value=30.5),
    ]

def test_get_climatology_by_month_range_and_location_ids(mock_climatology_data):
    with patch("aclimate_v3_orm.services.climate_historical_climatology_service.ClimateHistoricalClimatologyService.get_by_location_id") as mock_get:
        def side_effect(location_id):
            return [d for d in mock_climatology_data if d.location_id == location_id]
        
        mock_get.side_effect = side_effect

        response = client.get(
            "/climatology/by-month-range-and-location-ids",
            params={"location_ids": "456,789", "start_month": 5, "end_month": 6}
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 2  

        for item in data:
            assert "id" in item
            assert "location_id" in item
            assert "location_name" in item
            assert "measure_id" in item
            assert "measure_name" in item
            assert "measure_short_name" in item
            assert "measure_unit" in item
            assert "month" in item
            assert "value" in item
            assert 5 <= item["month"] <= 6

from fastapi.testclient import TestClient
import os
import sys
import pytest
from unittest.mock import patch

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from main import app

client = TestClient(app)

@pytest.fixture
def mock_climatology_data():
    class Measure:
        def __init__(self, id, name, short_name, unit):
            self.id = id
            self.name = name
            self.short_name = short_name
            self.unit = unit

    class Location:
        def __init__(self, id, name):
            self.id = id
            self.name = name

    class Climatology:
        def __init__(self, id, location_id, location, measure_id, measure, month, value):
            self.id = id
            self.location_id = location_id
            self.location = location
            self.measure_id = measure_id
            self.measure = measure
            self.month = month
            self.value = value

    location1 = Location(1, "Palmira")
    location2 = Location(2, "Cali")
    measure1 = Measure(10, "Precipitación", "prec", "mm")
    measure2 = Measure(11, "Temperatura", "temp", "°C")

    return {
        1: [
            Climatology(101, 1, location1, 10, measure1, 3, 123.4),
            Climatology(102, 1, location1, 11, measure2, 4, 26.1),
        ],
        2: [
            Climatology(201, 2, location2, 10, measure1, 5, 111.0),
            Climatology(202, 2, location2, 11, measure2, 6, 28.0),
        ]
    }

def test_get_climatology_by_month_range_location_ids_all_measures(mock_climatology_data):
    def mock_get_by_location_id(loc_id):
        return mock_climatology_data.get(loc_id, [])

    with patch("aclimate_v3_orm.services.climate_historical_climatology_service.ClimateHistoricalClimatologyService.get_by_location_id", side_effect=mock_get_by_location_id):
        response = client.get(
            "/climatology/by-month-range-location-ids-all-measures",
            params={"location_ids": "1,2", "start_month": 3, "end_month": 5}
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert all("location_id" in d for d in data)
        assert all(3 <= d["month"] <= 5 for d in data)
        assert {d["location_id"] for d in data} == {1, 2}

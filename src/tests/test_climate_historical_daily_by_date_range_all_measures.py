from fastapi.testclient import TestClient
import pytest
from datetime import date
from unittest.mock import patch
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from main import app

client = TestClient(app)

@pytest.fixture
def mock_daily_data():
    class Location:
        def __init__(self, id, name):
            self.id = id
            self.name = name

    class Measure:
        def __init__(self, id, name, short_name, unit):
            self.id = id
            self.name = name
            self.short_name = short_name
            self.unit = unit

    class ClimateRecord:
        def __init__(self, id, location_id, location, measure_id, measure, date, value):
            self.id = id
            self.location_id = location_id
            self.location = location
            self.measure_id = measure_id
            self.measure = measure
            self.date = date
            self.value = value

    loc = Location(1, "Palmira")
    m1 = Measure(1, "Precipitación", "ppt", "mm")
    m2 = Measure(2, "Temperatura", "tavg", "°C")

    return [
        ClimateRecord(1, 1, loc, 1, m1, date(2025, 5, 3), 10.0),
        ClimateRecord(2, 1, loc, 2, m2, date(2025, 5, 12), 28.5),
        ClimateRecord(3, 1, loc, 1, m1, date(2025, 6, 1), 15.0),  
    ]

def test_get_by_date_range_all_measures(mock_daily_data):
    with patch("aclimate_v3_orm.services.climate_historical_daily_service.ClimateHistoricalDailyService.get_by_location_id", return_value=mock_daily_data):
        response = client.get(
            "/historical-daily/climate/by-date-range-all-measures",
            params={
                "location_ids": "1",
                "start_date": "2025-05-01",
                "end_date": "2025-05-26"
            }
        )

        assert response.status_code == 200
        data = response.json()

        assert isinstance(data, list)
        assert len(data) == 2 

        for record in data:
            assert "id" in record
            assert "location_id" in record
            assert "location_name" in record
            assert "measure_id" in record
            assert "measure_name" in record
            assert "measure_short_name" in record
            assert "measure_unit" in record
            assert "date" in record
            assert "value" in record

        dates = [r["date"] for r in data]
        assert "2025-06-01" not in dates

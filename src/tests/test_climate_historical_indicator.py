from fastapi.testclient import TestClient
import os
import sys
import pytest
from unittest.mock import patch

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from main import app

client = TestClient(app)

@pytest.fixture
def mock_historical_indicator_data():
    class Indicator:
        def __init__(self, id, name, short_name, unit):
            self.id = id
            self.name = name
            self.short_name = short_name
            self.unit = unit
    class Location:
        def __init__(self, id, name):
            self.id = id
            self.name = name
    class Record:
        def __init__(self, id, indicator, location, value, period, start_date, end_date):
            self.id = id
            self.indicator_id = indicator.id
            self.indicator = indicator
            self.location_id = location.id
            self.location = location
            self.value = value
            self.period = period
            self.start_date = start_date
            self.end_date = end_date
    indicator = Indicator(1, "consecutive_rainy_days", "crd", "days")
    location = Location(10, "Palmira")
    return [
        Record(100, indicator, location, 5, "MONTHLY", "2024-01-01", "2024-01-31"),
        Record(101, indicator, location, 7, "MONTHLY", "2024-02-01", "2024-02-28")
    ]

def test_get_historical_by_location_id(mock_historical_indicator_data):
    with patch("aclimate_v3_orm.services.climate_historical_indicator_service.ClimateHistoricalIndicatorService.get_by_location_id", return_value=mock_historical_indicator_data):
        response = client.get("/indicator/by-location-id", params={"location_id": 10})
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 2
        for item in data:
            assert "id" in item
            assert "indicator_id" in item
            assert "indicator_name" in item
            assert "indicator_short_name" in item
            assert "indicator_unit" in item
            assert "location_id" in item
            assert "location_name" in item
            assert "value" in item
            assert "period" in item
            assert "start_date" in item
            assert "end_date" in item
            assert item["location_id"] == 10

def test_get_historical_by_period(mock_historical_indicator_data):
    with patch("aclimate_v3_orm.services.climate_historical_indicator_service.ClimateHistoricalIndicatorService.get_by_period", return_value=mock_historical_indicator_data):
        response = client.get("/indicator/by-period", params={"period": "monthly"})
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 2
        for item in data:
            assert "id" in item
            assert "indicator_id" in item
            assert "indicator_name" in item
            assert "indicator_short_name" in item
            assert "indicator_unit" in item
            assert "location_id" in item
            assert "location_name" in item
            assert "value" in item
            assert "period" in item
            assert "start_date" in item
            assert "end_date" in item
            assert item["period"].upper() == "MONTHLY"

def test_get_historical_by_indicator_name(mock_historical_indicator_data):
    with patch("aclimate_v3_orm.services.climate_historical_indicator_service.ClimateHistoricalIndicatorService.get_by_indicator_name", return_value=mock_historical_indicator_data):
        response = client.get("/indicator/by-indicator-name", params={"indicator_name": "consecutive_rainy_days"})
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 2
        for item in data:
            assert "indicator_name" in item
            assert item["indicator_name"] == "consecutive_rainy_days"

def test_get_historical_by_location_and_indicator_name(mock_historical_indicator_data):
    with patch("aclimate_v3_orm.services.climate_historical_indicator_service.ClimateHistoricalIndicatorService.get_by_location_and_indicator_name", return_value=mock_historical_indicator_data):
        response = client.get("/indicator/by-location-and-indicator-name", params={"location_name": "Palmira", "indicator_name": "consecutive_rainy_days"})
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 2
        for item in data:
            assert "location_name" in item
            assert item["location_name"] == "Palmira"
            assert "indicator_name" in item
            assert item["indicator_name"] == "consecutive_rainy_days"

def test_get_historical_by_date_range(mock_historical_indicator_data):
    with patch("aclimate_v3_orm.services.climate_historical_indicator_service.ClimateHistoricalIndicatorService.get_by_date_range", return_value=mock_historical_indicator_data):
        response = client.get("/indicator/by-date-range", params={"start_date": "2024-01-01", "end_date": "2024-02-28"})
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 2
        for item in data:
            assert "start_date" in item
            assert "end_date" in item

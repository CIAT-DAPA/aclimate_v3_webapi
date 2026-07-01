import pytest
from datetime import date
from unittest.mock import patch

from conftest import client, MockIndicator, MockLocation, MockIndicatorRecord


@pytest.fixture
def mock_historical_indicator_data():
    indicator = MockIndicator(1, "consecutive_rainy_days", "crd", "days")
    location = MockLocation(10, "Palmira", "EXT10", "palmira", True, None)
    return [
        MockIndicatorRecord(100, indicator, location, 5, "MONTHLY", "2024-01-01", "2024-01-31"),
        MockIndicatorRecord(101, indicator, location, 7, "MONTHLY", "2024-02-01", "2024-02-28")
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
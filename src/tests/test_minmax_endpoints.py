from unittest.mock import patch

from conftest import client


def test_minmax_indicator_by_location():
    mock_data = [
        {"indicator_id": 1, "indicator_name": "CRD", "location_id": 10, "location_name": "Palmira",
         "min_value": 2.0, "min_start_date": "2024-01-01", "max_value": 10.0, "max_end_date": "2024-06-01"},
        {"indicator_id": 2, "indicator_name": "TMAX", "location_id": 10, "location_name": "Palmira",
         "min_value": 25.0, "min_start_date": "2024-03-01", "max_value": 35.0, "max_end_date": "2024-09-01"},
    ]
    with patch("aclimate_v3_orm.services.climate_historical_indicator_service.ClimateHistoricalIndicatorService.get_max_min_by_location_id", return_value=mock_data):
        response = client.get("/indicator/minmax-by-location", params={"location_id": 10})
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 2
        for item in data:
            assert "id" in item
            assert "name" in item
            assert "min_value" in item
            assert "max_value" in item


def test_minmax_daily_by_location():
    mock_data = [
        {"measure_id": 1, "measure_name": "Precipitación", "location_id": 10, "location_name": "Palmira",
         "min_value": 0.0, "min_date": "2024-01-01", "max_value": 50.0, "max_date": "2024-06-01"},
    ]
    with patch("aclimate_v3_orm.services.climate_historical_daily_service.ClimateHistoricalDailyService.get_max_min_by_location_id", return_value=mock_data):
        response = client.get("/historical-daily/minmax-by-location", params={"location_id": 10})
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 1
        for item in data:
            assert "id" in item
            assert "name" in item
            assert "min_value" in item
            assert "max_value" in item


def test_minmax_monthly_by_location():
    mock_data = [
        {"measure_id": 1, "measure_name": "Precipitación", "location_id": 10, "location_name": "Palmira",
         "min_value": 10.0, "min_date": "2024-01-01", "max_value": 200.0, "max_date": "2024-06-01"},
    ]
    with patch("aclimate_v3_orm.services.climate_historical_monthly_service.ClimateHistoricalMonthlyService.get_max_min_by_location_id", return_value=mock_data):
        response = client.get("/historical-monthly/minmax-by-location", params={"location_id": 10})
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 1
        for item in data:
            assert "id" in item
            assert "name" in item
            assert "min_value" in item
            assert "max_value" in item


def test_minmax_climatology_by_location():
    mock_data = [
        {"measure_id": 1, "measure_name": "Precipitación", "location_id": 10, "location_name": "Palmira",
         "min_value": 30.0, "min_month": 1, "max_value": 150.0, "max_month": 7},
    ]
    with patch("aclimate_v3_orm.services.climate_historical_climatology_service.ClimateHistoricalClimatologyService.get_max_min_by_location_id", return_value=mock_data):
        response = client.get("/climatology/minmax-by-location", params={"location_id": 10})
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 1
        for item in data:
            assert "id" in item
            assert "name" in item
            assert "min_value" in item
            assert "max_value" in item
            assert "min_month" in item
            assert "max_month" in item
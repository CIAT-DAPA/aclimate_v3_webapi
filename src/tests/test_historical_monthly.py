import pytest
from datetime import date
from unittest.mock import patch

from conftest import client, MockLocation, MockMeasure, MockRecord


@pytest.fixture
def mock_monthly_data():
    loc = MockLocation(1, "Palmira", "EXT1", "palmira", True, None)
    m1 = MockMeasure(1, "Precipitación", "ppt", "mm")
    m2 = MockMeasure(2, "Temperatura", "tavg", "°C")

    return [
        MockRecord(1, 1, loc, 1, m1, date(2025, 5, 1), 100.0),
        MockRecord(2, 1, loc, 2, m2, date(2025, 5, 1), 26.5),
        MockRecord(3, 1, loc, 1, m1, date(2025, 6, 1), 150.0),
    ]


def test_get_historical_monthly_by_date_range_all_measures(mock_monthly_data):
    with patch("aclimate_v3_orm.services.ClimateHistoricalMonthlyService.get_by_location_id", return_value=mock_monthly_data):
        response = client.get(
            "/historical-monthly/by-date-range-all-measures",
            params={
                "location_ids": "1",
                "start_date": "2025-05-01",
                "end_date": "2025-05-31"
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
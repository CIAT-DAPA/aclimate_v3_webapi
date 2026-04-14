# test_get_climatology_date_ranges_by_location_ids.py

import os
import sys
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from main import app

client = TestClient(app)

@pytest.fixture
def mock_locations():
    class Location:
        def __init__(self, id, name):
            self.id = id
            self.name = name

    return [
        Location(id=1, name="Loc A"),
        Location(id=2, name="Loc B"),
        Location(id=3, name="Loc C"),
    ]

@pytest.fixture
def mock_date_ranges():
    return {
        1: {"min_month": 1, "max_month": 12},
        2: {"min_month": 3, "max_month": 10},
        3: {"min_month": None, "max_month": None},  
    }

def test_get_climatology_date_ranges_by_location_ids(mock_locations, mock_date_ranges):
    with patch("aclimate_v3_orm.services.climate_historical_climatology_service.ClimateHistoricalClimatologyService.get_date_range_by_location_id") as mock_get_range, \
         patch("aclimate_v3_orm.services.mng_location_service.MngLocationService.get_all_enable", return_value=mock_locations):

        # Simular comportamiento de get_date_range_by_location_id según ID
        def range_side_effect(loc_id):
            return mock_date_ranges.get(loc_id, {"min_month": None, "max_month": None})
        mock_get_range.side_effect = range_side_effect

        response = client.get("/climatology/by-location-ids-date-range", params={"location_ids": "1,2,3"})
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 2  

        for entry in data:
            assert "id" in entry
            assert "name" in entry
            assert "min_month" in entry
            assert "max_month" in entry
            assert entry["min_month"] is not None
            assert entry["max_month"] is not None

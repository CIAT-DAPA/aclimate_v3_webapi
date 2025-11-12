from fastapi.testclient import TestClient
import os
import sys
import pytest
from unittest.mock import patch

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from main import app

client = TestClient(app)

@pytest.fixture
def mock_mng_indicator_data():
    class Indicator:
        def __init__(self, id, name, short_name, unit, type_, temporality, indicator_category_id, description, enable, registered_at, updated_at):
            self.id = id
            self.name = name
            self.short_name = short_name
            self.unit = unit
            self.type = type_
            self.temporality = temporality
            self.indicator_category_id= indicator_category_id
            self.description = description
            self.enable = enable
            self.registered_at = registered_at
            self.updated_at = updated_at
    return [
        Indicator(1, "consecutive_rainy_days", "crd", "days", "CLIMATE", "MONTHLY", 1, "desc", True, "2024-01-01T00:00:00", "2024-01-02T00:00:00"),
        Indicator(2, "precipitation", "prec", "mm", "CLIMATE", "MONTHLY", 1, "desc", True, "2024-01-01T00:00:00", "2024-01-02T00:00:00")
    ]

def test_get_mng_by_name(mock_mng_indicator_data):
    with patch("aclimate_v3_orm.services.mng_indicators_service.MngIndicatorService.get_by_name", return_value=mock_mng_indicator_data):
        response = client.get("/indicator-mng/by-name", params={"name": "consecutive_rainy_days"})
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 2
        for item in data:
            assert "name" in item
            assert "short_name" in item
            assert "unit" in item
            assert "type" in item
            assert "temporality" in item
            assert "indicator_category_id" in item
            assert "description" in item
            assert "enable" in item
            assert "registered_at" in item
            assert "updated_at" in item

def test_get_mng_by_short_name(mock_mng_indicator_data):
    with patch("aclimate_v3_orm.services.mng_indicators_service.MngIndicatorService.get_by_short_name", return_value=mock_mng_indicator_data):
        response = client.get("/indicator-mng/by-short-name", params={"short_name": "crd"})
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 2
        for item in data:
            assert "short_name" in item
            assert item["short_name"] == "crd" or item["short_name"] == "prec"

def test_get_mng_by_type(mock_mng_indicator_data):
    with patch("aclimate_v3_orm.services.mng_indicators_service.MngIndicatorService.get_by_type", return_value=mock_mng_indicator_data):
        response = client.get("/indicator-mng/by-type", params={"type": "CLIMATE"})
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 2
        for item in data:
            assert "type" in item
            assert item["type"] == "CLIMATE"

def test_get_mng_all_enabled(mock_mng_indicator_data):
    with patch("aclimate_v3_orm.services.mng_indicators_service.MngIndicatorService.get_all_enabled", return_value=mock_mng_indicator_data):
        response = client.get("/indicator-mng/all-enabled")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 2
        for item in data:
            assert "enable" in item
            assert item["enable"] is True

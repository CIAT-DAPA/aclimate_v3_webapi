import pytest
from unittest.mock import patch, MagicMock

from conftest import client, MockIndicator, MockIndicatorCategory


# --- /indicator-mng/all-categories ---

def test_get_all_categories():
    mock_data = [
        MockIndicatorCategory(1, "Temperaturas Extremas", "Descripción"),
        MockIndicatorCategory(2, "Estrés Hídrico", "Descripción"),
    ]
    with patch("aclimate_v3_orm.services.mng_indicator_category_service.MngIndicatorCategoryService.get_all", return_value=mock_data):
        response = client.get("/indicator-mng/all-categories")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 2
        for item in data:
            assert "id" in item
            assert "name" in item
            assert "description" in item
            assert "enable" in item


# --- /indicator-mng/by-category-id ---

@patch("routes.get_mng_indicators.MngIndicatorService")
def test_get_indicators_by_category_id(mock_service_class):
    mock_instance = MagicMock()
    mock_service_class.return_value = mock_instance
    mock_instance.get_by_category_id.return_value = [
        MockIndicator(1, "Días fríos", "TX10p", "% días/año", indicator_category_id=1),
        MockIndicator(2, "Días cálidos", "TX90p", "% días/año", indicator_category_id=1),
    ]

    response = client.get("/indicator-mng/by-category-id", params={"category_id": 1})
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 2
    for item in data:
        assert item["indicator_category_id"] == 1
        assert "id" in item
        assert "name" in item
        assert "short_name" in item
        assert "unit" in item
        assert "type" in item
        assert "temporality" in item


# --- /indicator-mng/by-country ---

@patch("routes.get_mng_indicators.MngIndicatorsFeaturesService")
@patch("routes.get_mng_indicators.MngIndicatorService")
@patch("routes.get_mng_indicators.MngCountryIndicatorService")
def test_get_indicators_by_country(mock_country_service_class, mock_indicator_service_class, mock_features_service_class):
    """Test the complex by-country endpoint which chains multiple services."""
    mock_country_instance = MagicMock()
    mock_country_service_class.return_value = mock_country_instance
    mock_indicator_instance = MagicMock()
    mock_indicator_service_class.return_value = mock_indicator_instance
    mock_features_instance = MagicMock()
    mock_features_service_class.return_value = mock_features_instance

    mock_country_instance.get_by_country.return_value = [
        MagicMock(indicator_id=1, id=100, description=None),
        MagicMock(indicator_id=2, id=101, description=None),
    ]

    # Use plain objects to avoid conflicts with builtin 'type' and 'id'
    class MockIndicatorObj:
        def __init__(self, oid, name, short_name, unit, indicator_type, temporality, indicator_category_id, description, enable):
            self.id = oid
            self.name = name
            self.short_name = short_name
            self.unit = unit
            self.type = indicator_type  # lowercase to match type.lower() in route
            self.temporality = temporality
            self.indicator_category_id = indicator_category_id
            self.description = description
            self.enable = enable

    def mock_get_by_id(indicator_id):
        mapping = {
            1: MockIndicatorObj(1, "Días fríos", "TX10p", "% días/año", "climate", "ANNUAL", 1, "Desc", True),
            2: MockIndicatorObj(2, "Días cálidos", "TX90p", "% días/año", "climate", "ANNUAL", 1, "Desc", True),
        }
        return mapping.get(indicator_id)
    mock_indicator_instance.get_by_id.side_effect = mock_get_by_id
    mock_features_instance.get_by_country_indicator.return_value = []

    response = client.get("/indicator-mng/by-country", params={"country_id": 1})
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 2
    for item in data:
        assert "features" in item
        assert isinstance(item["features"], list)
from unittest.mock import patch, MagicMock

from conftest import client


# --- /indicator-category-mng/by-category ---

def test_get_category_by_id():
    """Test GET /indicator-category-mng/by-category?category_id=1"""
    mock_data = MagicMock()
    mock_data.id = 1
    mock_data.name = "Temperaturas Extremas"
    mock_data.description = "Descripción"
    mock_data.enable = True
    mock_data.registered_at = "2024-01-01T00:00:00"
    mock_data.updated_at = "2024-01-01T00:00:00"

    with patch("routes.get_mng_indicator_categories.MngIndicatorCategoryService") as mock_service_class:
        mock_instance = MagicMock()
        mock_service_class.return_value = mock_instance
        mock_instance.get_by_id.return_value = mock_data

        response = client.get("/indicator-category-mng/by-category", params={"category_id": 1})
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert data["id"] == 1
        assert data["name"] == "Temperaturas Extremas"


# --- /indicator-category-mng/by-country ---

def test_get_categories_by_country():
    """Test GET /indicator-category-mng/by-country?country_id=1"""
    with \
      patch("routes.get_mng_indicator_categories.MngCountryIndicatorService") as mock_country_class, \
      patch("routes.get_mng_indicator_categories.MngIndicatorService") as mock_indicator_class, \
      patch("routes.get_mng_indicator_categories.MngIndicatorCategoryService") as mock_category_class:

        # Setup mocks
        mock_country_instance = MagicMock()
        mock_country_class.return_value = mock_country_instance
        mock_indicator_instance = MagicMock()
        mock_indicator_class.return_value = mock_indicator_instance
        mock_category_instance = MagicMock()
        mock_category_class.return_value = mock_category_instance

        # Country indicators service returns 2 indicators
        mock_country_instance.get_by_country.return_value = [
            MagicMock(indicator_id=1),
            MagicMock(indicator_id=2),
        ]

        # Indicator service returns indicators with category IDs
        def mock_get_by_id(indicator_id):
            return MagicMock(indicator_category_id=indicator_id, enable=True)
        mock_indicator_instance.get_by_id.side_effect = mock_get_by_id

        # Category service returns categories
        def mock_get_by_id_cat(category_id):
            cat = MagicMock()
            cat.id = category_id
            cat.name = "Category " + str(category_id)
            cat.description = "Desc " + str(category_id)
            cat.enable = True
            cat.registered_at = "2024-01-01T00:00:00"
            cat.updated_at = "2024-01-01T00:00:00"
            return cat
        mock_category_instance.get_by_id.side_effect = mock_get_by_id_cat

        response = client.get("/indicator-category-mng/by-country", params={"country_id": 1})
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 2
        for item in data:
            assert "id" in item
            assert "name" in item
            assert "description" in item
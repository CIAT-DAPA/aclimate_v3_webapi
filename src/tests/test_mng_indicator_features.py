from unittest.mock import patch, MagicMock

from conftest import client


# --- /indicator-features/by-indicator-and-country ---

def test_get_features_by_indicator_and_country():
    mock_country_indicator = MagicMock(id=200)
    mock_features = [
        MagicMock(id=1, country_indicator_id=200, title="Feature 1", description="Desc 1", type="recommendation"),
        MagicMock(id=2, country_indicator_id=200, title="Feature 2", description="Desc 2", type="feature"),
    ]

    with \
      patch("aclimate_v3_orm.services.mng_country_indicator_service.MngCountryIndicatorService.get_by_country_and_indicator", return_value=mock_country_indicator), \
      patch("aclimate_v3_orm.services.mng_indicators_features_service.MngIndicatorsFeaturesService.get_by_country_indicator", return_value=mock_features):

        response = client.get(
            "/indicator-features/by-indicator-and-country",
            params={"indicator_id": 1, "country_id": 1}
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 2
        for item in data:
            assert "id" in item
            assert "title" in item
            assert "description" in item
            assert "type" in item


def test_get_features_by_indicator_and_country_with_type_filter():
    mock_country_indicator = MagicMock(id=200)
    mock_features = [
        MagicMock(id=1, country_indicator_id=200, title="Feature 1", description="Desc 1", type="recommendation"),
    ]

    with \
      patch("aclimate_v3_orm.services.mng_country_indicator_service.MngCountryIndicatorService.get_by_country_and_indicator", return_value=mock_country_indicator), \
      patch("aclimate_v3_orm.services.mng_indicators_features_service.MngIndicatorsFeaturesService.get_by_country_indicator_and_type", return_value=mock_features):

        response = client.get(
            "/indicator-features/by-indicator-and-country",
            params={"indicator_id": 1, "country_id": 1, "type": "recommendation"}
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 1


def test_get_features_not_found():
    with patch("aclimate_v3_orm.services.mng_country_indicator_service.MngCountryIndicatorService.get_by_country_and_indicator", return_value=None):
        response = client.get(
            "/indicator-features/by-indicator-and-country",
            params={"indicator_id": 999, "country_id": 999}
        )
        assert response.status_code == 404
from unittest.mock import patch

from conftest import client


def test_get_countries_by_name(mock_countries):
    with patch("aclimate_v3_orm.services.mng_country_service.MngCountryService.get_by_name", return_value=mock_countries):
        response = client.get("/countries/by-name", params={"name": "Colombia"})
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 2
        for item in data:
            assert "id" in item
            assert "name" in item
            assert "iso2" in item
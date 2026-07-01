from unittest.mock import patch, MagicMock

from conftest import client, MockMeasure


def test_get_climate_measures_by_country():
    mock_measure_1 = MockMeasure(1, "Precipitación", "prec", "mm", "Precipitación total acumulada")
    mock_measure_1.enable = True
    mock_measure_2 = MockMeasure(2, "Temperatura", "tavg", "°C", "Temperatura media")
    mock_measure_2.enable = True
    mock_data = [
        MagicMock(measure=mock_measure_1),
        MagicMock(measure=mock_measure_2),
    ]

    with patch("aclimate_v3_orm.services.mng_country_climate_measure_service.MngCountryClimateMeasureService.get_by_country", return_value=mock_data):
        response = client.get("/countries/1/climate-measures")
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 2
        for item in data:
            assert "id" in item
            assert "name" in item
            assert "short_name" in item
            assert "unit" in item
            assert "description" in item
            assert "enable" not in item

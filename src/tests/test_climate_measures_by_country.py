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


def test_get_country_climate_measure_configuration():
    mock_measure_1 = MockMeasure(1, "Precipitación", "prec", "mm", "Precipitación total acumulada")
    mock_measure_1.enable = True
    mock_measure_2 = MockMeasure(2, "Temperatura", "tavg", "°C", "Temperatura media")
    mock_measure_2.enable = True
    mock_measure_disabled = MockMeasure(3, "Humedad", "rhum", "%", "Humedad relativa")
    mock_measure_disabled.enable = False

    # Config with a mix of plain strings and enum-like objects with .value
    mock_data = [
        MagicMock(
            id=11,
            country_id=1,
            measure_id=1,
            spatial_forecast=True,
            spatial_climate=True,
            location_forecast=False,
            location_climate=True,
            spatial_climate_conf=[
                {
                    "temporality": "daily",
                    "store": "climate_historical_daily_ni_prec",
                    "workspace": "climate_historical_daily",
                },
                {
                    "temporality": "monthly",
                    "store": "climate_historical_monthly_ni_prec",
                    "workspace": "climate_historical_monthly",
                },
            ],
            location_climate_conf=["daily", "monthly", "climatology"],
            description="Config Precipitación",
            measure=mock_measure_1,
        ),
        MagicMock(
            id=12,
            country_id=1,
            measure_id=2,
            spatial_forecast=False,
            spatial_climate=True,
            location_forecast=True,
            location_climate=False,
            spatial_climate_conf=[
                MagicMock(temporality=MagicMock(value="annual"), store=None, workspace=None),
            ],
            location_climate_conf=[MagicMock(value="annual")],
            description=None,
            measure=mock_measure_2,
        ),
        MagicMock(
            id=13,
            country_id=1,
            measure_id=3,
            spatial_forecast=False,
            spatial_climate=False,
            location_forecast=False,
            location_climate=False,
            spatial_climate_conf=None,
            location_climate_conf=None,
            description=None,
            measure=mock_measure_disabled,
        ),
    ]

    with patch("aclimate_v3_orm.services.mng_country_climate_measure_service.MngCountryClimateMeasureService.get_by_country", return_value=mock_data):
        response = client.get("/countries/1/climate-measures/configuration")
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 2  # disabled measure filtered out

        config_map = {item["id"]: item for item in data}

        first = config_map[11]
        assert first["country_id"] == 1
        assert first["measure_id"] == 1
        assert first["spatial_forecast"] is True
        assert first["spatial_climate"] is True
        assert first["location_forecast"] is False
        assert first["location_climate"] is True
        assert first["spatial_climate_conf"] == [
            {
                "temporality": "daily",
                "store": "climate_historical_daily_ni_prec",
                "workspace": "climate_historical_daily",
            },
            {
                "temporality": "monthly",
                "store": "climate_historical_monthly_ni_prec",
                "workspace": "climate_historical_monthly",
            },
        ]
        assert first["location_climate_conf"] == ["daily", "monthly", "climatology"]
        assert first["description"] == "Config Precipitación"
        # Old fields (temporality/store/workspace) must no longer appear in the response
        assert "temporality" not in first
        assert "store" not in first
        assert "workspace" not in first

        second = config_map[12]
        # List containing a single enum-like object -> serialized to ["annual"]
        assert second["spatial_climate_conf"] == [
            {"temporality": "annual", "store": None, "workspace": None}
        ]
        assert second["location_climate_conf"] == ["annual"]
        assert second["description"] is None
        assert "temporality" not in second
        assert "store" not in second
        assert "workspace" not in second

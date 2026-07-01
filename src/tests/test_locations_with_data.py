from unittest.mock import patch, MagicMock
from datetime import date

from conftest import client, MockCountry, MockAdmin1, MockAdmin2, MockLocation


@patch("routes.get_locations_with_data.ClimateHistoricalDailyService")
@patch("routes.get_locations_with_data.MngLocationService")
def test_get_locations_with_data(mock_location_service_class, mock_climate_service_class):
    mock_location_instance = MagicMock()
    mock_location_service_class.return_value = mock_location_instance
    mock_climate_instance = MagicMock()
    mock_climate_service_class.return_value = mock_climate_instance

    country = MockCountry(1, "Colombia", "CO")
    admin1 = MockAdmin1(10, "Cundinamarca", country, "11")
    admin2 = MockAdmin2(20, "Bogotá", admin1, "11001")
    location = MockLocation(101, "Test Location", "EXT101", "test_machine_name", True, admin2,
                            123.45, 4.5, -74.1, "IDEAM", source_id=1)

    mock_location_instance.get_by_country_id.return_value = [location]

    mock_latest_data = {
        "date": date(2025, 5, 15),
        "measures": [
            {
                "measure_id": 1, "measure_name": "Precipitación",
                "measure_short_name": "prec", "measure_unit": "mm", "value": 10.5
            }
        ]
    }

    mock_climate_instance.get_latest_by_location.return_value = mock_latest_data

    response = client.get("/locations/by-country-ids-with-data", params={"country_ids": "1", "days": 30})
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 1

    loc = data[0]
    assert loc["id"] == 101
    assert loc["name"] == "Test Location"
    assert loc["country_id"] == 1
    assert loc["country_name"] == "Colombia"
    assert loc["admin2_id"] == 20
    assert loc["admin1_id"] == 10
    assert loc["source_id"] == 1
    assert loc["source_name"] == "IDEAM"
    assert loc["source_type"] == "weather_station"
    assert loc["latest_data"] is not None
    assert loc["latest_data"]["date"] == "2025-05-15"
    assert len(loc["latest_data"]["measures"]) == 1
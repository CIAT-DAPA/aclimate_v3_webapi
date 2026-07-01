from unittest.mock import patch

from conftest import client, MockCountry, MockAdmin1, MockAdmin2, MockLocation


def test_get_locations_by_id():
    country = MockCountry(1, "Colombia", "CO")
    admin1 = MockAdmin1(10, "Cundinamarca", country, "11")
    admin2 = MockAdmin2(20, "Bogotá", admin1, "11001")
    mock_location = MockLocation(101, "Test Location", "EXT101", "test_machine_name", True, admin2,
                                 123.45, 4.5, -74.1, "IDEAM")

    with patch("aclimate_v3_orm.services.mng_location_service.MngLocationService.get_by_id", return_value=mock_location):
        response = client.get("/locations/by-id", params={"id": 101})

        assert response.status_code == 200
        loc = response.json()
        assert loc["id"] == 101
        assert loc["name"] == "Test Location"
        assert loc["ext_id"] == "EXT101"
        assert loc["machine_name"] == "test_machine_name"
        assert loc["admin2_id"] == 20
        assert loc["admin2_name"] == "Bogotá"
        assert loc["admin1_id"] == 10
        assert loc["admin1_name"] == "Cundinamarca"
        assert loc["country_id"] == 1
        assert loc["country_name"] == "Colombia"
        assert loc["country_iso2"] == "CO"
        assert loc["source"] == "IDEAM"
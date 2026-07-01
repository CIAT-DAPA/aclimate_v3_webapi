from unittest.mock import patch

from conftest import client


def test_get_locations_by_name(mock_locations):
    with patch("aclimate_v3_orm.services.mng_location_service.MngLocationService.get_by_name", return_value=mock_locations):
        response = client.get("/locations/by-name", params={"name": "Test Location"})

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 1

        loc = data[0]
        assert loc["id"] == 101
        assert loc["name"] == "Test Location"
        assert loc["ext_id"] == "EXT101"
        assert loc["visible"] is True
        assert loc["admin2_id"] == 20
        assert loc["admin2_name"] == "Bogotá"
        assert loc["admin2_ext_id"] == "11001"
        assert loc["admin1_id"] == 10
        assert loc["admin1_name"] == "Cundinamarca"
        assert loc["admin1_ext_id"] == "11"
        assert loc["country_id"] == 1
        assert loc["country_name"] == "Colombia"
        assert loc["country_iso2"] == "CO"
        assert loc["machine_name"] == "test_machine_name"
        assert loc["source"] == "IDEAM"
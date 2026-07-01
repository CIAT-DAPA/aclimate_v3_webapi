from unittest.mock import patch

from conftest import client


def test_get_admin1_by_country_ids(mock_admin1_data):
    with patch("aclimate_v3_orm.services.mng_admin_1_service.MngAdmin1Service.get_by_country_id") as mock_method:
        mock_method.side_effect = lambda cid: mock_admin1_data.get(cid, [])

        response = client.get("/admin1/by-country-ids", params={"country_ids": "1,2"})
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 2

        expected = {
            101: {"name": "Antioquia", "ext_id": "05", "country_id": 1, "country_name": "Colombia", "country_iso2": "CO"},
            201: {"name": "Pichincha", "ext_id": "17", "country_id": 2, "country_name": "Ecuador", "country_iso2": "EC"},
        }

        for item in data:
            assert item["id"] in expected
            expected_item = expected[item["id"]]
            assert item["name"] == expected_item["name"]
            assert item["ext_id"] == expected_item["ext_id"]
            assert item["country_id"] == expected_item["country_id"]
            assert item["country_name"] == expected_item["country_name"]
            assert item["country_iso2"] == expected_item["country_iso2"]
from unittest.mock import patch

from conftest import client


def test_get_admin1_by_name(mock_admin1_list):
    filtered = [a for a in mock_admin1_list if "anti" in a.name.lower()]
    with patch("aclimate_v3_orm.services.mng_admin_1_service.MngAdmin1Service.get_by_name", return_value=filtered):
        response = client.get("/admin1/by-name", params={"name": "anti"})
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 2

        for item in data:
            assert "id" in item
            assert "name" in item
            assert "ext_id" in item
            assert "country_id" in item
            assert "country_name" in item
            assert "country_iso2" in item
            assert "anti" in item["name"].lower()
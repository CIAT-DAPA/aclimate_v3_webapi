from unittest.mock import patch

from conftest import client


def test_get_admin2_by_name(mock_admin2_list):
    with patch("aclimate_v3_orm.services.mng_admin_2_service.MngAdmin2Service.get_by_name", return_value=mock_admin2_list):
        response = client.get("/admin2/by-name", params={"name": "Cauca"})
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 2

        for item in data:
            assert "id" in item
            assert "name" in item
            assert "ext_id" in item
            assert "admin1_id" in item
            assert "admin1_name" in item
            assert "admin1_ext_id" in item
            assert "country_id" in item
            assert "country_name" in item
            assert "country_iso2" in item
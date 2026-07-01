from unittest.mock import patch

from conftest import client, MockCountry, MockAdmin1, MockAdmin2


def test_get_admin2_by_country_ids():
    country = MockCountry(id=1, name="Colombia", iso2="CO")
    admin1 = MockAdmin1(id=101, name="Pacifico", country=country, ext_id="76")
    mock_data = {
        1: [
            MockAdmin2(id=302, name="Valle del Cauca", admin_1=admin1, ext_id="76001"),
            MockAdmin2(id=303, name="Cauca", admin_1=admin1, ext_id="19001"),
        ]
    }

    with patch("aclimate_v3_orm.services.mng_admin_2_service.MngAdmin2Service.get_by_country_id") as mock_method:
        mock_method.side_effect = lambda cid: mock_data.get(cid, [])

        response = client.get("/admin2/by-country-ids", params={"country_ids": "1"})
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
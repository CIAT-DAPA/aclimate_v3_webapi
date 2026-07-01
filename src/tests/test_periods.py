import pytest
from unittest.mock import patch, MagicMock

from conftest import client


def test_get_available_periods():
    """Test /periods/available which queries the database directly."""
    # We need to mock SessionLocal and the query chain
    # The endpoint uses `session.query(exists().where(...)).scalar()`
    with patch("routes.get_available_periods.SessionLocal") as mock_session_local:
        mock_session = MagicMock()
        mock_session_local.return_value = mock_session
        # Mock scalar() to return True for daily/monthly, False for others
        mock_scalar = MagicMock()
        mock_scalar.scalar.side_effect = [True, True, False, False, False, False]
        mock_session.query.return_value = mock_scalar

        response = client.get("/periods/available", params={"location_id": 1})
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 6

        period_map = {p["value"]: p["has_data"] for p in data}
        assert period_map["daily"] is True
        assert period_map["monthly"] is True
        assert period_map["annual"] is False
        assert period_map["seasonal"] is False
        assert period_map["decadal"] is False
        assert period_map["other"] is False
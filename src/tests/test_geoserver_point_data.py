from unittest.mock import patch

import numpy as np
import pytest
from rasterio.io import MemoryFile
from rasterio.transform import from_origin

from conftest import client
from services.geoserver import build_climatology_time_subset, generate_climatology_month_list

DOWNLOAD_RASTER = "routes.get_geoserver_point_data.download_raster"
GEOSERVER_AUTH = "routes.get_geoserver_point_data.get_geoserver_auth"

# Point inside the test raster (lon, lat)
POINT = [-86.55, 12.55]


def _build_geotiff(value: float) -> bytes:
    """Build an in-memory GeoTIFF (EPSG:4326, lon [-87, -86], lat [12, 13]) filled with a value."""
    data = np.full((10, 10), value, dtype="float32")
    with MemoryFile() as memfile:
        with memfile.open(
            driver="GTiff", height=10, width=10, count=1, dtype="float32",
            crs="EPSG:4326", transform=from_origin(-87.0, 13.0, 0.1, 0.1), nodata=-9999.0,
        ) as dataset:
            dataset.write(data, 1)
        return memfile.read()


def _fake_download(workspace, store, time_subset, session=None):
    """Simulate GeoServer: the raster value is the month of the requested time subset."""
    # time_subset looks like: Time("2000-03-01T00:00:00.000Z") -> month 3
    month = int(time_subset.split("-")[1])
    return time_subset, _build_geotiff(float(month))


def _request_body(**overrides) -> dict:
    """Build a valid climatology request body, overriding the fields given as keyword arguments."""
    body = {
        "coordinates": [POINT],
        "start_date": "01",
        "end_date": "03",
        "workspace": "climate_historical_climatology",
        "store": "climate_historical_climatology_ni_prec",
        "temporality": "climatology",
    }
    body.update(overrides)
    return body


@pytest.fixture(autouse=True)
def mock_geoserver_auth():
    """Avoid requiring real GeoServer credentials in the tests."""
    with patch(GEOSERVER_AUTH, return_value=("user", "password")):
        yield


# ---------- Service ----------

def test_build_climatology_time_subset_uses_reference_year():
    assert build_climatology_time_subset(3) == 'Time("2000-03-01T00:00:00.000Z")'


def test_generate_climatology_month_list_returns_months_in_mm_format():
    assert generate_climatology_month_list(11, 12) == [
        {"date_str": "11", "time_subset": 'Time("2000-11-01T00:00:00.000Z")'},
        {"date_str": "12", "time_subset": 'Time("2000-12-01T00:00:00.000Z")'},
    ]


# ---------- Endpoint: climatology ----------

def test_point_data_climatology_returns_one_value_per_month_in_mm_format():
    with patch(DOWNLOAD_RASTER, side_effect=_fake_download) as mock_download:
        response = client.post("/geoserver/point-data", json=_request_body())

    assert response.status_code == 200
    # One result per month, identified by the month in MM format and sorted
    assert response.json() == {
        "total_results": 3,
        "data": [
            {"coordinate": POINT, "date": "01", "value": 1.0},
            {"coordinate": POINT, "date": "02", "value": 2.0},
            {"coordinate": POINT, "date": "03", "value": 3.0},
        ],
    }

    # The rasters are requested to GeoServer with the reference year of the climatology
    requested = sorted(call.args[2] for call in mock_download.call_args_list)
    assert requested == [
        'Time("2000-01-01T00:00:00.000Z")',
        'Time("2000-02-01T00:00:00.000Z")',
        'Time("2000-03-01T00:00:00.000Z")',
    ]


def test_point_data_climatology_without_end_date_returns_single_month():
    body = _request_body(start_date="07")
    del body["end_date"]
    with patch(DOWNLOAD_RASTER, side_effect=_fake_download):
        response = client.post("/geoserver/point-data", json=body)

    assert response.status_code == 200
    assert response.json()["data"] == [{"coordinate": POINT, "date": "07", "value": 7.0}]


def test_point_data_climatology_full_year():
    with patch(DOWNLOAD_RASTER, side_effect=_fake_download):
        response = client.post("/geoserver/point-data", json=_request_body(start_date="01", end_date="12"))

    assert response.status_code == 200
    assert [item["date"] for item in response.json()["data"]] == [f"{month:02d}" for month in range(1, 13)]


@pytest.mark.parametrize("overrides", [
    # Months out of range or not zero-padded
    {"start_date": "00"},
    {"end_date": "13"},
    {"start_date": "1"},
    # Full dates are not valid for climatology
    {"start_date": "2024-01-01", "end_date": "2024-03-01"},
    # The range must not end before it starts
    {"start_date": "05", "end_date": "02"},
])
def test_point_data_climatology_returns_422_for_invalid_months(overrides):
    with patch(DOWNLOAD_RASTER, side_effect=_fake_download) as mock_download:
        response = client.post("/geoserver/point-data", json=_request_body(**overrides))

    assert response.status_code == 422
    mock_download.assert_not_called()


# ---------- Endpoint: other temporalities keep working with dates ----------

def test_point_data_daily_still_works_with_dates():
    with patch(DOWNLOAD_RASTER, side_effect=_fake_download):
        response = client.post(
            "/geoserver/point-data",
            json=_request_body(start_date="2024-05-01", end_date="2024-05-02", temporality="daily"),
        )

    assert response.status_code == 200
    assert response.json() == {
        "total_results": 2,
        "data": [
            {"coordinate": POINT, "date": "2024-05-01", "value": 5.0},
            {"coordinate": POINT, "date": "2024-05-02", "value": 5.0},
        ],
    }


def test_point_data_monthly_still_works_with_dates():
    with patch(DOWNLOAD_RASTER, side_effect=_fake_download):
        response = client.post(
            "/geoserver/point-data",
            json=_request_body(start_date="2024-11-15", end_date="2025-01-15", temporality="monthly"),
        )

    assert response.status_code == 200
    assert [item["date"] for item in response.json()["data"]] == ["2024-11-01", "2024-12-01", "2025-01-01"]


@pytest.mark.parametrize("overrides", [
    # Months are only valid for climatology
    {"start_date": "01", "end_date": "03", "temporality": "daily"},
    {"start_date": "2024-01-01", "end_date": "03", "temporality": "monthly"},
    # The range must not end before it starts
    {"start_date": "2024-01-10", "end_date": "2024-01-01", "temporality": "daily"},
])
def test_point_data_returns_422_for_invalid_dates(overrides):
    with patch(DOWNLOAD_RASTER, side_effect=_fake_download) as mock_download:
        response = client.post("/geoserver/point-data", json=_request_body(**overrides))

    assert response.status_code == 422
    mock_download.assert_not_called()

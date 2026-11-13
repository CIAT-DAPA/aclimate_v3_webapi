import io
import zipfile
from unittest.mock import patch

import numpy as np
import pytest
import rasterio
from rasterio.io import MemoryFile
from rasterio.transform import from_origin

from conftest import client

DOWNLOAD_RASTER = "routes.get_geoserver_polygon_data.download_raster"
GEOSERVER_AUTH = "routes.get_geoserver_polygon_data.get_geoserver_auth"

# Source raster: 10x10 pixels of 0.1 degrees covering lon [-87, -86] and lat [12, 13]
RASTER_WEST, RASTER_NORTH, PIXEL_SIZE, RASTER_SIZE = -87.0, 13.0, 0.1, 10

# Polygon covering lon [-86.75, -86.45] and lat [12.35, 12.65] (inside the raster)
POLYGON = {
    "type": "Polygon",
    "coordinates": [[
        [-86.75, 12.35], [-86.45, 12.35], [-86.45, 12.65], [-86.75, 12.65], [-86.75, 12.35]
    ]],
}

# Polygon completely outside the raster extent
POLYGON_OUTSIDE = {
    "type": "Polygon",
    "coordinates": [[[10.0, 10.0], [11.0, 10.0], [11.0, 11.0], [10.0, 11.0], [10.0, 10.0]]],
}


def _build_geotiff() -> bytes:
    """Build an in-memory GeoTIFF (EPSG:4326) whose pixel values are 0..99."""
    data = np.arange(RASTER_SIZE * RASTER_SIZE, dtype="float32").reshape(RASTER_SIZE, RASTER_SIZE)
    with MemoryFile() as memfile:
        with memfile.open(
            driver="GTiff", height=RASTER_SIZE, width=RASTER_SIZE, count=1, dtype="float32",
            crs="EPSG:4326", transform=from_origin(RASTER_WEST, RASTER_NORTH, PIXEL_SIZE, PIXEL_SIZE),
            nodata=-9999.0,
        ) as dataset:
            dataset.write(data, 1)
        return memfile.read()


def _fake_download(workspace, store, time_subset, session=None):
    """Simulate GeoServer returning the same raster for every date."""
    return time_subset, _build_geotiff()


def _request_body(polygon=POLYGON, **overrides) -> dict:
    """Build a valid request body, overriding the fields given as keyword arguments."""
    body = {
        "polygon": polygon,
        "start_date": "2024-01-01",
        "end_date": "2024-01-03",
        "workspace": "climate_historical_daily",
        "store": "climate_historical_daily_ni_prec",
        "temporality": "daily",
    }
    body.update(overrides)
    return body


def _read_zip(content: bytes) -> dict:
    """Return a dict {file name: file bytes} with the files of a ZIP."""
    with zipfile.ZipFile(io.BytesIO(content)) as zip_file:
        return {name: zip_file.read(name) for name in zip_file.namelist()}


@pytest.fixture(autouse=True)
def mock_geoserver_auth():
    """Avoid requiring real GeoServer credentials in the tests."""
    with patch(GEOSERVER_AUTH, return_value=("user", "password")):
        yield


def test_polygon_data_returns_zip_with_one_clipped_raster_per_date():
    with patch(DOWNLOAD_RASTER, side_effect=_fake_download) as mock_download:
        response = client.post("/geoserver/polygon-data", json=_request_body())

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/zip"

    # One raster is downloaded and returned per date of the range
    assert mock_download.call_count == 3
    files = _read_zip(response.content)
    assert sorted(files) == ["2024-01-01.tif", "2024-01-02.tif", "2024-01-03.tif"]

    # Every raster is cropped to the pixels touched by the polygon
    for content in files.values():
        with MemoryFile(content) as memfile, memfile.open() as raster:
            assert raster.crs.to_string() == "EPSG:4326"
            # The polygon touches 4x4 pixels: lon [-86.8, -86.4], lat [12.3, 12.7]
            assert (raster.width, raster.height) == (4, 4)
            assert raster.bounds.left == pytest.approx(-86.8)
            assert raster.bounds.right == pytest.approx(-86.4)
            assert raster.bounds.bottom == pytest.approx(12.3)
            assert raster.bounds.top == pytest.approx(12.7)
            # Values are the ones of the source raster (rows 3-6, columns 2-5)
            expected = np.arange(100, dtype="float32").reshape(10, 10)[3:7, 2:6]
            np.testing.assert_array_equal(raster.read(1), expected)


def test_polygon_data_masks_pixels_outside_the_polygon():
    # Triangle: the pixels of its bounding box that it does not touch must be nodata
    triangle = {
        "type": "Polygon",
        "coordinates": [[[-86.95, 12.05], [-86.05, 12.05], [-86.95, 12.95], [-86.95, 12.05]]],
    }
    with patch(DOWNLOAD_RASTER, side_effect=_fake_download):
        response = client.post(
            "/geoserver/polygon-data",
            json=_request_body(polygon=triangle, end_date="2024-01-01"),
        )

    assert response.status_code == 200
    content = _read_zip(response.content)["2024-01-01.tif"]
    with MemoryFile(content) as memfile, memfile.open() as raster:
        data = raster.read(1)
        # Bottom-left corner is inside the triangle, top-right corner is outside
        assert data[-1, 0] != raster.nodata
        assert data[0, -1] == raster.nodata


@pytest.mark.parametrize("geojson", [
    {"type": "Feature", "properties": {"name": "farm"}, "geometry": POLYGON},
    {"type": "FeatureCollection", "features": [{"type": "Feature", "properties": {}, "geometry": POLYGON}]},
    {"type": "MultiPolygon", "coordinates": [POLYGON["coordinates"]]},
])
def test_polygon_data_accepts_feature_collection_and_multipolygon(geojson):
    with patch(DOWNLOAD_RASTER, side_effect=_fake_download):
        response = client.post(
            "/geoserver/polygon-data",
            json=_request_body(polygon=geojson, end_date="2024-01-01"),
        )

    assert response.status_code == 200
    assert list(_read_zip(response.content)) == ["2024-01-01.tif"]


def test_polygon_data_polygon_smaller_than_a_pixel_returns_data():
    # Polygon of 0.01 degrees inside a single 0.1 degrees pixel
    small = {
        "type": "Polygon",
        "coordinates": [[[-86.56, 12.52], [-86.55, 12.52], [-86.55, 12.53], [-86.56, 12.53], [-86.56, 12.52]]],
    }
    with patch(DOWNLOAD_RASTER, side_effect=_fake_download):
        response = client.post(
            "/geoserver/polygon-data",
            json=_request_body(polygon=small, end_date="2024-01-01"),
        )

    assert response.status_code == 200
    content = _read_zip(response.content)["2024-01-01.tif"]
    with MemoryFile(content) as memfile, memfile.open() as raster:
        assert (raster.width, raster.height) == (1, 1)


def test_polygon_data_monthly_temporality_uses_first_day_of_month():
    with patch(DOWNLOAD_RASTER, side_effect=_fake_download):
        response = client.post(
            "/geoserver/polygon-data",
            json=_request_body(start_date="2024-01-15", end_date="2024-03-15", temporality="monthly"),
        )

    assert response.status_code == 200
    assert sorted(_read_zip(response.content)) == ["2024-01-01.tif", "2024-02-01.tif", "2024-03-01.tif"]


def test_polygon_data_skips_dates_without_raster():
    def download_only_second_day(workspace, store, time_subset, session=None):
        """Simulate GeoServer having data only for 2024-01-02."""
        return time_subset, _build_geotiff() if "2024-01-02" in time_subset else None

    with patch(DOWNLOAD_RASTER, side_effect=download_only_second_day):
        response = client.post("/geoserver/polygon-data", json=_request_body())

    assert response.status_code == 200
    assert list(_read_zip(response.content)) == ["2024-01-02.tif"]


def test_polygon_data_returns_404_when_no_raster_is_available():
    with patch(DOWNLOAD_RASTER, side_effect=lambda w, s, t, session=None: (t, None)):
        response = client.post("/geoserver/polygon-data", json=_request_body())

    assert response.status_code == 404
    assert response.json()["detail"] == "No data found for the given polygon and dates"


def test_polygon_data_returns_404_when_polygon_is_outside_the_raster():
    with patch(DOWNLOAD_RASTER, side_effect=_fake_download):
        response = client.post("/geoserver/polygon-data", json=_request_body(polygon=POLYGON_OUTSIDE))

    assert response.status_code == 404


@pytest.mark.parametrize("geojson", [
    {"type": "Point", "coordinates": [-86.5, 12.5]},
    {"type": "Feature", "properties": {}, "geometry": {"type": "Point", "coordinates": [-86.5, 12.5]}},
    {"type": "Feature", "properties": {}, "geometry": None},
    {"type": "FeatureCollection", "features": []},
    {"type": "Polygon", "coordinates": [[[-86.5, 12.5], [-86.4, 12.5]]]},
    # Self-intersecting polygon (bow tie)
    {"type": "Polygon", "coordinates": [[[0, 0], [1, 1], [1, 0], [0, 1], [0, 0]]]},
    {"foo": "bar"},
])
def test_polygon_data_returns_400_for_invalid_polygon(geojson):
    with patch(DOWNLOAD_RASTER, side_effect=_fake_download) as mock_download:
        response = client.post("/geoserver/polygon-data", json=_request_body(polygon=geojson))

    assert response.status_code == 400
    assert response.json()["detail"].startswith("Invalid polygon")
    # GeoServer is never queried when the polygon is not valid
    mock_download.assert_not_called()


def test_polygon_data_returns_422_when_end_date_is_before_start_date():
    response = client.post(
        "/geoserver/polygon-data",
        json=_request_body(start_date="2024-01-10", end_date="2024-01-01"),
    )
    assert response.status_code == 422


def test_polygon_data_returns_422_when_polygon_is_missing():
    body = _request_body()
    del body["polygon"]
    response = client.post("/geoserver/polygon-data", json=body)
    assert response.status_code == 422

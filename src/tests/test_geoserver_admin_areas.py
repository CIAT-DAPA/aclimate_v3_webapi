from unittest.mock import patch
from urllib.parse import parse_qs, urlparse

import pytest
import requests

from conftest import client
from services import geoserver as geoserver_service
from services.geoserver import (
    GeoServerRequestError,
    build_text_search_cql,
    get_wfs_features,
    get_wfs_layer_text_fields,
    list_wfs_layers,
)

ROUTE = "routes.get_geoserver_admin_areas"

# WFS capabilities with three layers of the "administrative" workspace
CAPABILITIES_XML = b"""<?xml version="1.0" encoding="UTF-8"?>
<wfs:WFS_Capabilities version="2.0.0" xmlns:wfs="http://www.opengis.net/wfs/2.0"
    xmlns:ows="http://www.opengis.net/ows/1.1">
  <ows:ServiceIdentification><ows:Title>WFS</ows:Title></ows:ServiceIdentification>
  <wfs:FeatureTypeList>
    <wfs:FeatureType><wfs:Name>administrative:sat_amazonia_area_drenajes</wfs:Name><wfs:Title>Drenajes</wfs:Title></wfs:FeatureType>
    <wfs:FeatureType><wfs:Name>administrative:colombia_adm1</wfs:Name><wfs:Title>Colombia</wfs:Title></wfs:FeatureType>
    <wfs:FeatureType><wfs:Name>administrative:et_adm3_wp</wfs:Name><wfs:Title>Ethiopia</wfs:Title></wfs:FeatureType>
  </wfs:FeatureTypeList>
</wfs:WFS_Capabilities>"""

# DescribeFeatureType answer: two text attributes, one number and the geometry
DESCRIBE_JSON = {
    "featureTypes": [
        {
            "typeName": "colombia_adm1",
            "properties": [
                {"name": "the_geom", "type": "gml:MultiPolygon", "localType": "MultiPolygon"},
                {"name": "ADM1_ES", "type": "xsd:string", "localType": "string"},
                {"name": "ADM1_PCODE", "type": "xsd:string", "localType": "string"},
                {"name": "AREA_SQKM", "type": "xsd:double", "localType": "double"},
            ],
        }
    ]
}

GEOMETRY = {
    "type": "MultiPolygon",
    "coordinates": [[[[-76.5, 3.1], [-76.4, 3.1], [-76.4, 3.2], [-76.5, 3.2], [-76.5, 3.1]]]],
}

# GetFeature answer as GeoServer returns it (with extra members and a record without geometry)
FEATURES_JSON = {
    "type": "FeatureCollection",
    "features": [
        {
            "type": "Feature",
            "id": "colombia_adm1.31",
            "geometry": GEOMETRY,
            "geometry_name": "the_geom",
            "properties": {"ADM1_ES": "Valle del Cauca", "ADM1_PCODE": "CO76", "AREA_SQKM": 20665.5},
        },
        {
            "type": "Feature",
            "id": "colombia_adm1.99",
            "geometry": None,
            "geometry_name": "the_geom",
            "properties": {"ADM1_ES": "Valle sin geometria", "ADM1_PCODE": "CO00", "AREA_SQKM": 0},
        },
    ],
    "totalFeatures": 2,
    "numberMatched": 2,
    "numberReturned": 2,
    "timeStamp": "2026-11-20T00:00:00.000Z",
    "crs": {"type": "name", "properties": {"name": "urn:ogc:def:crs:EPSG::4326"}},
}


class FakeResponse:
    """Minimal requests.Response double."""

    def __init__(self, status_code=200, content=b"", json_data=None):
        self.status_code = status_code
        self.content = content
        self.text = content.decode("utf-8", errors="ignore")
        self._json_data = json_data

    def json(self):
        """Return the configured JSON or fail like requests does with non-JSON bodies."""
        if self._json_data is None:
            raise ValueError("No JSON object could be decoded")
        return self._json_data

    def raise_for_status(self):
        """Raise an HTTPError for error status codes, like requests does."""
        if self.status_code >= 400:
            raise requests.exceptions.HTTPError(f"{self.status_code} Server Error")


class FakeSession:
    """requests.Session double that records the requested URLs and returns queued responses."""

    def __init__(self, responses):
        self.responses = list(responses)
        self.urls = []

    def get(self, url, timeout=None):
        """Record the URL and return the next queued response (or raise it if it is an exception)."""
        self.urls.append(url)
        response = self.responses.pop(0)
        if isinstance(response, Exception):
            raise response
        return response

    def query(self, index=0):
        """Return the query parameters of a recorded request as a dict of single values."""
        return {key: values[0] for key, values in parse_qs(urlparse(self.urls[index]).query).items()}


@pytest.fixture(autouse=True)
def clean_geoserver_state():
    """Start every test with an empty layer cache and configured GeoServer credentials."""
    geoserver_service.clear_wfs_layers_cache()
    with patch(f"{ROUTE}.get_geoserver_auth", return_value=("user", "password")):
        yield
    geoserver_service.clear_wfs_layers_cache()


# ---------- Service: WFS helpers ----------

def test_list_wfs_layers_parses_capabilities_and_sorts_names():
    session = FakeSession([FakeResponse(content=CAPABILITIES_XML)])

    layers = list_wfs_layers("administrative", session)

    assert layers == ["colombia_adm1", "et_adm3_wp", "sat_amazonia_area_drenajes"]
    assert "/administrative/ows?" in session.urls[0]
    assert session.query() == {"service": "WFS", "version": "2.0.0", "request": "GetCapabilities"}


def test_list_wfs_layers_uses_cache_until_cleared():
    session = FakeSession([FakeResponse(content=CAPABILITIES_XML), FakeResponse(content=CAPABILITIES_XML)])

    list_wfs_layers("administrative", session)
    list_wfs_layers("administrative", session)
    # The second call is served from the cache
    assert len(session.urls) == 1

    geoserver_service.clear_wfs_layers_cache()
    list_wfs_layers("administrative", session)
    assert len(session.urls) == 2


@pytest.mark.parametrize("response", [
    FakeResponse(status_code=500),
    requests.exceptions.ConnectionError("connection refused"),
    FakeResponse(content=b"this is not xml"),
])
def test_list_wfs_layers_raises_when_geoserver_fails(response):
    with pytest.raises(GeoServerRequestError):
        list_wfs_layers("administrative", FakeSession([response]))


def test_get_wfs_layer_text_fields_returns_only_string_attributes():
    session = FakeSession([FakeResponse(json_data=DESCRIBE_JSON)])

    fields = get_wfs_layer_text_fields("administrative", "colombia_adm1", session)

    assert fields == ["ADM1_ES", "ADM1_PCODE"]
    query = session.query()
    assert query["request"] == "DescribeFeatureType"
    assert query["typeNames"] == "administrative:colombia_adm1"
    assert query["outputFormat"] == "application/json"


def test_build_text_search_cql_searches_every_field():
    cql = build_text_search_cql(["ADM1_ES", "ADM1_PCODE"], "Cauca")

    assert cql == "\"ADM1_ES\" ILIKE '%Cauca%' OR \"ADM1_PCODE\" ILIKE '%Cauca%'"


def test_build_text_search_cql_escapes_quotes_and_wildcards():
    # A quote must not close the string and % / _ must be searched literally
    cql = build_text_search_cql(["name"], "O'Higgins 100%_x\\")

    assert cql == "\"name\" ILIKE '%O''Higgins 100\\%\\_x\\\\%'"


def test_get_wfs_features_requests_geojson_in_lon_lat():
    session = FakeSession([FakeResponse(json_data=FEATURES_JSON)])

    data = get_wfs_features("administrative", "colombia_adm1", "\"ADM1_ES\" ILIKE '%valle%'", 100, session)

    assert data == FEATURES_JSON
    query = session.query()
    assert query["request"] == "GetFeature"
    assert query["typeNames"] == "administrative:colombia_adm1"
    assert query["outputFormat"] == "application/json"
    assert query["srsName"] == "EPSG:4326"
    assert query["cql_filter"] == "\"ADM1_ES\" ILIKE '%valle%'"
    assert query["count"] == "100"


def test_get_wfs_features_raises_when_answer_is_not_json():
    # GeoServer reports WFS errors as an XML document with status 200
    session = FakeSession([FakeResponse(content=b"<ows:ExceptionReport/>")])

    with pytest.raises(GeoServerRequestError):
        get_wfs_features("administrative", "colombia_adm1", session=session)


# ---------- Endpoint: /geoserver/admin-areas/layers ----------

def test_admin_area_layers_returns_prefix_and_level():
    layers = ["colombia_adm0", "et_adm3_wp", "pe_adm2", "sat_amazonia_adm1", "sat_amazonia_area_drenajes"]
    with patch(f"{ROUTE}.list_wfs_layers", return_value=layers) as mock_list:
        response = client.get("/geoserver/admin-areas/layers")

    assert response.status_code == 200
    assert response.json() == [
        {"layer": "colombia_adm0", "prefix": "colombia", "level": 0},
        {"layer": "et_adm3_wp", "prefix": "et", "level": 3},
        {"layer": "pe_adm2", "prefix": "pe", "level": 2},
        {"layer": "sat_amazonia_adm1", "prefix": "sat_amazonia", "level": 1},
        # Layers outside the naming convention have no prefix and no level
        {"layer": "sat_amazonia_area_drenajes", "prefix": None, "level": None},
    ]
    # The layers are always read from the administrative workspace
    mock_list.assert_called_once_with("administrative")


def test_admin_area_layers_returns_502_when_geoserver_fails():
    with patch(f"{ROUTE}.list_wfs_layers", side_effect=GeoServerRequestError("GeoServer WFS request failed: down")):
        response = client.get("/geoserver/admin-areas/layers")

    assert response.status_code == 502
    assert "GeoServer WFS request failed" in response.json()["detail"]


# ---------- Endpoint: /geoserver/admin-areas/polygon ----------

def _polygon_patches(features=FEATURES_JSON, text_fields=("ADM1_ES", "ADM1_PCODE")):
    """Patch the GeoServer calls of the polygon endpoint and return the three patchers."""
    return (
        patch(f"{ROUTE}.list_wfs_layers", return_value=["colombia_adm1", "pe_adm1"]),
        patch(f"{ROUTE}.get_wfs_layer_text_fields", return_value=list(text_fields)),
        patch(f"{ROUTE}.get_wfs_features", return_value=features),
    )


def test_admin_area_polygon_returns_geojson_with_layer_attributes():
    list_patch, fields_patch, features_patch = _polygon_patches()
    with list_patch, fields_patch as mock_fields, features_patch as mock_features:
        response = client.get(
            "/geoserver/admin-areas/polygon",
            params={"layer": "colombia_adm1", "description": "  valle  "},
        )

    assert response.status_code == 200
    # Clean GeoJSON: only the record with geometry and only standard members
    assert response.json() == {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "id": "colombia_adm1.31",
                "geometry": GEOMETRY,
                "properties": {"ADM1_ES": "Valle del Cauca", "ADM1_PCODE": "CO76", "AREA_SQKM": 20665.5},
            }
        ],
    }

    # The description is searched (trimmed) in every text attribute of the layer
    mock_fields.assert_called_once_with("administrative", "colombia_adm1")
    mock_features.assert_called_once_with(
        "administrative",
        "colombia_adm1",
        "\"ADM1_ES\" ILIKE '%valle%' OR \"ADM1_PCODE\" ILIKE '%valle%'",
        100,
    )


def test_admin_area_polygon_searches_the_fields_of_each_layer():
    # Another layer with different attribute names
    list_patch, fields_patch, features_patch = _polygon_patches(text_fields=("NOMBDEP", "CCDD"))
    with list_patch, fields_patch, features_patch as mock_features:
        response = client.get(
            "/geoserver/admin-areas/polygon",
            params={"layer": "pe_adm1", "description": "Cusco"},
        )

    assert response.status_code == 200
    assert mock_features.call_args.args[2] == "\"NOMBDEP\" ILIKE '%Cusco%' OR \"CCDD\" ILIKE '%Cusco%'"


def test_admin_area_polygon_result_can_be_used_in_polygon_data():
    from routes.get_geoserver_polygon_data import extract_polygon_geometries

    list_patch, fields_patch, features_patch = _polygon_patches()
    with list_patch, fields_patch, features_patch:
        response = client.get(
            "/geoserver/admin-areas/polygon",
            params={"layer": "colombia_adm1", "description": "valle"},
        )

    # The FeatureCollection is a valid "polygon" for /geoserver/polygon-data
    geometries = extract_polygon_geometries(response.json())
    assert len(geometries) == 1
    assert geometries[0]["type"] == "MultiPolygon"


def test_admin_area_polygon_escapes_quotes_in_description():
    list_patch, fields_patch, features_patch = _polygon_patches(text_fields=("name",))
    with list_patch, fields_patch, features_patch as mock_features:
        client.get(
            "/geoserver/admin-areas/polygon",
            params={"layer": "colombia_adm1", "description": "x' OR '1'='1"},
        )

    # The quotes are doubled, so the text stays inside the string literal
    assert mock_features.call_args.args[2] == "\"name\" ILIKE '%x'' OR ''1''=''1%'"


def test_admin_area_polygon_returns_404_when_layer_does_not_exist():
    list_patch, fields_patch, features_patch = _polygon_patches()
    with list_patch, fields_patch as mock_fields, features_patch as mock_features:
        response = client.get(
            "/geoserver/admin-areas/polygon",
            params={"layer": "other_workspace:secret_layer", "description": "valle"},
        )

    assert response.status_code == 404
    assert response.json()["detail"] == "Layer 'other_workspace:secret_layer' not found"
    # GeoServer is not queried for layers outside the administrative workspace
    mock_fields.assert_not_called()
    mock_features.assert_not_called()


@pytest.mark.parametrize("features", [
    {"type": "FeatureCollection", "features": []},
    # Records that match but have no geometry are not polygons
    {"type": "FeatureCollection", "features": [{"type": "Feature", "id": "a.1", "geometry": None, "properties": {}}]},
])
def test_admin_area_polygon_returns_404_when_nothing_matches(features):
    list_patch, fields_patch, features_patch = _polygon_patches(features=features)
    with list_patch, fields_patch, features_patch:
        response = client.get(
            "/geoserver/admin-areas/polygon",
            params={"layer": "colombia_adm1", "description": "Atlantis"},
        )

    assert response.status_code == 404
    assert response.json()["detail"] == "No polygon found in layer 'colombia_adm1' for description 'Atlantis'"


def test_admin_area_polygon_returns_404_when_layer_has_no_text_attributes():
    list_patch, fields_patch, features_patch = _polygon_patches(text_fields=())
    with list_patch, fields_patch, features_patch as mock_features:
        response = client.get(
            "/geoserver/admin-areas/polygon",
            params={"layer": "colombia_adm1", "description": "valle"},
        )

    assert response.status_code == 404
    mock_features.assert_not_called()


@pytest.mark.parametrize("params", [
    {"layer": "colombia_adm1"},
    {"description": "valle"},
    {"layer": "colombia_adm1", "description": ""},
    {"layer": "colombia_adm1", "description": "   "},
])
def test_admin_area_polygon_returns_422_when_parameters_are_missing_or_empty(params):
    list_patch, fields_patch, features_patch = _polygon_patches()
    with list_patch, fields_patch, features_patch as mock_features:
        response = client.get("/geoserver/admin-areas/polygon", params=params)

    assert response.status_code == 422
    mock_features.assert_not_called()


def test_admin_area_polygon_returns_502_when_geoserver_fails():
    list_patch, fields_patch, _ = _polygon_patches()
    with list_patch, fields_patch, \
         patch(f"{ROUTE}.get_wfs_features", side_effect=GeoServerRequestError("GeoServer did not return GeoJSON")):
        response = client.get(
            "/geoserver/admin-areas/polygon",
            params={"layer": "colombia_adm1", "description": "valle"},
        )

    assert response.status_code == 502


def test_admin_area_endpoints_use_real_service_end_to_end():
    # Full flow through the service with a fake GeoServer session
    session = FakeSession([
        FakeResponse(content=CAPABILITIES_XML),
        FakeResponse(json_data=DESCRIBE_JSON),
        FakeResponse(json_data=FEATURES_JSON),
    ])
    with patch("services.geoserver.get_geoserver_session", return_value=session):
        response = client.get(
            "/geoserver/admin-areas/polygon",
            params={"layer": "colombia_adm1", "description": "Valle"},
        )

    assert response.status_code == 200
    assert len(response.json()["features"]) == 1
    # Capabilities, attributes and features are requested in that order
    assert [session.query(i)["request"] for i in range(3)] == [
        "GetCapabilities", "DescribeFeatureType", "GetFeature",
    ]
    assert session.query(2)["cql_filter"] == "\"ADM1_ES\" ILIKE '%Valle%' OR \"ADM1_PCODE\" ILIKE '%Valle%'"

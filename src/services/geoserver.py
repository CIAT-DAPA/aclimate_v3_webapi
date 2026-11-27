"""
Shared GeoServer service module.

Centralizes:
- GeoServer connection configuration (URL, auth, HTTP session with connection pool)
- Date generation logic (daily/monthly/annual)
- WCS URL building
- Raster download with shared session
- Adaptive date limits based on temporality
- Structured logging
- WFS access to vector layers (layer list, text attributes and feature search)
"""

import logging
import os
import time
import xml.etree.ElementTree as ET
from datetime import date, timedelta
from typing import Any, Dict, List, Literal, Optional, Tuple
from urllib.parse import urlencode

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# ---------- Logger ----------
logger = logging.getLogger(__name__)

# ---------- Configuration from environment ----------
GEOSERVER_URL = os.getenv("GEOSERVER_URL", "https://geo.aclimate.org/geoserver/")
GEOSERVER_USER = os.getenv("GEOSERVER_USER")
GEOSERVER_PASSWORD = os.getenv("GEOSERVER_PASSWORD")
MAX_WORKERS = int(os.getenv("MAX_WORKERS", "4"))
# Workspace that holds the administrative areas (adm0 = country, adm1, adm2, ...)
GEOSERVER_ADMIN_WORKSPACE = os.getenv("GEOSERVER_ADMIN_WORKSPACE", "administrative")
# Maximum number of polygons returned by a single administrative area search
GEOSERVER_ADMIN_MAX_FEATURES = int(os.getenv("GEOSERVER_ADMIN_MAX_FEATURES", "100"))

# ---------- Constants ----------
# Maximum dates allowed per temporality (sync mode)
MAX_DATES_BY_TEMPORALITY: Dict[str, int] = {
    "daily": 7,
    "monthly": 12,
    "annual": 12,
}

DEFAULT_TIMEOUT = 60  # seconds

# Year used by the climatology mosaics in their time dimension (see build_climatology_time_subset)
CLIMATOLOGY_REFERENCE_YEAR = 2000

# WFS version used for vector layers
WFS_VERSION = "2.0.0"
# CRS of the returned features. The short "EPSG:4326" form makes GeoServer
# answer with longitude/latitude axis order, as GeoJSON requires.
WFS_OUTPUT_CRS = "EPSG:4326"
# Seconds the list of layers of a workspace is kept in memory
WFS_LAYERS_CACHE_TTL = 300


# ---------- Auth ----------
def get_geoserver_auth() -> Tuple[str, str]:
    """Return basic auth tuple from environment variables."""
    if not GEOSERVER_USER or not GEOSERVER_PASSWORD:
        logger.error("GeoServer credentials not configured in environment")
        from fastapi import HTTPException
        raise HTTPException(status_code=500, detail="GeoServer credentials not configured in environment")
    return (GEOSERVER_USER, GEOSERVER_PASSWORD)


def get_geoserver_url() -> str:
    """Return normalized GeoServer base URL (always ends with '/')."""
    return GEOSERVER_URL.rstrip('/') + '/'


# ---------- HTTP Session with connection pooling ----------
def create_geoserver_session() -> requests.Session:
    """
    Create a requests.Session with:
    - Connection pooling (up to 20 connections)
    - Retry strategy (3 retries, backoff factor 0.5)
    - Preconfigured basic auth
    - Longer timeout
    """
    session = requests.Session()

    # Auth
    if GEOSERVER_USER and GEOSERVER_PASSWORD:
        session.auth = (GEOSERVER_USER, GEOSERVER_PASSWORD)

    # Retry strategy
    retries = Retry(
        total=3,
        backoff_factor=0.5,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET"],
    )

    # Mount adapters with connection pool and retry
    adapter = HTTPAdapter(
        pool_connections=10,
        pool_maxsize=20,
        max_retries=retries,
    )
    session.mount("http://", adapter)
    session.mount("https://", adapter)

    return session


# Thread-local storage for session reuse across threads
import threading
_thread_local = threading.local()


def get_geoserver_session() -> requests.Session:
    """Get or create a thread-local GeoServer session."""
    if not hasattr(_thread_local, "session"):
        _thread_local.session = create_geoserver_session()
    return _thread_local.session


# ---------- Date generation ----------
def generate_date_list(start: date, end: date, temporality: str) -> List[Dict[str, str]]:
    """
    Generate a list of date info dictionaries from start to end,
    stepping by day, month, or year according to temporality.

    Each dict has:
        - "date_str": ISO-formatted date string (e.g. "2024-01-15")
        - "time_subset": WCS time subset parameter string
    """
    dates = []
    current = start
    while current <= end:
        year = current.year
        month = current.month
        day = current.day

        if temporality == "daily":
            time_subset = f"Time(\"{year:04d}-{month:02d}-{day:02d}T00:00:00.000Z\")"
            date_str = f"{year:04d}-{month:02d}-{day:02d}"
            current += timedelta(days=1)
        elif temporality == "monthly":
            time_subset = f"Time(\"{year:04d}-{month:02d}-01T00:00:00.000Z\")"
            date_str = f"{year:04d}-{month:02d}-01"
            if month == 12:
                current = current.replace(year=year + 1, month=1)
            else:
                current = current.replace(month=month + 1)
        elif temporality == "annual":
            time_subset = f"Time(\"{year:04d}-01-01T00:00:00.000Z\")"
            date_str = f"{year:04d}-01-01"
            current = current.replace(year=year + 1)
        else:
            raise ValueError(f"Unknown temporality: {temporality}")

        dates.append({"date_str": date_str, "time_subset": time_subset})

    return dates


def build_climatology_time_subset(month: int) -> str:
    """
    Build the WCS time subset that selects the climatology raster of a month.

    - month: Month number (1 to 12).
    """
    ###AJUSTAR FORMATO CLIMATOLOGY###
    # Today the climatology mosaics are published in GeoServer with a full date that uses
    # CLIMATOLOGY_REFERENCE_YEAR as year (2000-01-01, 2000-02-01, ...). When they are
    # published only by month (01, 02, 03, ...), this is the only place to change:
    # return the subset that selects the month in the new format.
    return f"Time(\"{CLIMATOLOGY_REFERENCE_YEAR:04d}-{month:02d}-01T00:00:00.000Z\")"


def generate_climatology_month_list(start_month: int, end_month: int) -> List[Dict[str, str]]:
    """
    Generate a list of month info dictionaries for the climatology, from start_month to end_month.

    Each dict has:
        - "date_str": Month in MM format (e.g. "01")
        - "time_subset": WCS time subset parameter string

    - start_month: First month of the range (1 to 12).
    - end_month: Last month of the range (1 to 12).
    """
    months = []
    # One entry per month of the range, both ends included
    for month in range(start_month, end_month + 1):
        months.append({
            "date_str": f"{month:02d}",
            "time_subset": build_climatology_time_subset(month),
        })
    return months


def get_max_dates_for_temporality(temporality: str) -> int:
    """Return the maximum number of dates allowed for the given temporality."""
    return MAX_DATES_BY_TEMPORALITY.get(temporality, 7)


# ---------- WCS URL building ----------
def build_wcs_url(workspace: str, store: str, time_subset: str) -> str:
    """
    Build a WCS GetCoverage URL for the given parameters.
    """
    url_root = get_geoserver_url()
    params = {
        "service": "WCS",
        "request": "GetCoverage",
        "version": "2.0.1",
        "coverageId": store,
        "format": "image/geotiff",
        "subset": time_subset,
    }
    return f"{url_root}{workspace}/ows?" + urlencode(params)


# ---------- Raster download ----------
def download_raster(
    workspace: str,
    store: str,
    time_subset: str,
    session: Optional[requests.Session] = None,
) -> Tuple[str, Optional[bytes]]:
    """
    Download a single raster from GeoServer.

    Returns a tuple of (time_subset, bytes_content).
    Returns (time_subset, None) if the raster is not found (404) or on error.
    """
    url = build_wcs_url(workspace, store, time_subset)
    if session is None:
        session = get_geoserver_session()

    try:
        resp = session.get(url, timeout=DEFAULT_TIMEOUT)
        if resp.status_code == 404:
            logger.warning("Raster not found (404) for coverage=%s, time=%s", store, time_subset)
            return time_subset, None
        resp.raise_for_status()
        logger.info("Downloaded raster for coverage=%s, time=%s (%d bytes)", store, time_subset, len(resp.content))
        return time_subset, resp.content
    except requests.exceptions.RequestException as e:
        logger.error("Error downloading raster for coverage=%s, time=%s: %s", store, time_subset, str(e))
        return time_subset, None


# ---------- WFS (vector layers) ----------
class GeoServerRequestError(Exception):
    """Raised when GeoServer cannot be reached or answers a WFS request with an error."""


# Cache of layer names per workspace: {workspace: (expiration time, layer names)}
_wfs_layers_cache: Dict[str, Tuple[float, List[str]]] = {}
_wfs_layers_cache_lock = threading.Lock()


def build_wfs_url(workspace: str, params: Dict[str, Any]) -> str:
    """
    Build a WFS URL for a workspace.

    - workspace: GeoServer workspace that owns the layers.
    - params: WFS query parameters (request, typeNames, cql_filter, ...).
      "service" and "version" are added automatically.
    """
    query = {"service": "WFS", "version": WFS_VERSION}
    query.update(params)
    return f"{get_geoserver_url()}{workspace}/ows?" + urlencode(query)


def _wfs_get(workspace: str, params: Dict[str, Any],
             session: Optional[requests.Session] = None) -> requests.Response:
    """
    Run a WFS GET request and return the response.

    - workspace: GeoServer workspace that owns the layers.
    - params: WFS query parameters.
    - session: Optional requests session (defaults to the thread-local one).

    Raises GeoServerRequestError on network errors or error status codes.
    """
    url = build_wfs_url(workspace, params)
    # Reuse the thread-local session when the caller does not provide one
    if session is None:
        session = get_geoserver_session()

    try:
        resp = session.get(url, timeout=DEFAULT_TIMEOUT)
        resp.raise_for_status()
    except requests.exceptions.RequestException as e:
        logger.error("WFS request failed (workspace=%s, request=%s): %s", workspace, params.get("request"), e)
        raise GeoServerRequestError(f"GeoServer WFS request failed: {e}")
    return resp


def clear_wfs_layers_cache() -> None:
    """Empty the in-memory cache of layer names (used by tests and after publishing layers)."""
    with _wfs_layers_cache_lock:
        _wfs_layers_cache.clear()


def list_wfs_layers(workspace: str, session: Optional[requests.Session] = None) -> List[str]:
    """
    Return the names of the vector layers published in a workspace, sorted alphabetically.

    The names do not include the workspace prefix (e.g. "colombia_adm1"). The result is
    cached in memory for WFS_LAYERS_CACHE_TTL seconds.

    - workspace: GeoServer workspace to inspect.
    - session: Optional requests session (defaults to the thread-local one).

    Raises GeoServerRequestError when GeoServer fails or its answer cannot be parsed.
    """
    now = time.monotonic()
    with _wfs_layers_cache_lock:
        cached = _wfs_layers_cache.get(workspace)
        # Serve the cached list while it has not expired
        if cached and cached[0] > now:
            return list(cached[1])

    resp = _wfs_get(workspace, {"request": "GetCapabilities"}, session)

    try:
        root = ET.fromstring(resp.content)
    except ET.ParseError as e:
        logger.error("Invalid WFS capabilities for workspace=%s: %s", workspace, e)
        raise GeoServerRequestError(f"Invalid WFS capabilities returned by GeoServer: {e}")

    layers = set()
    # Go through every XML element looking for the FeatureType entries
    for element in root.iter():
        # Only FeatureType elements describe a layer (tags are namespaced: "{ns}FeatureType")
        if element.tag.rsplit("}", 1)[-1] != "FeatureType":
            continue
        # Look for the Name child of the FeatureType
        for child in element:
            # The Name holds "workspace:layer"; keep only the layer part
            if child.tag.rsplit("}", 1)[-1] == "Name" and child.text:
                layers.add(child.text.strip().split(":", 1)[-1])

    result = sorted(layers)
    with _wfs_layers_cache_lock:
        _wfs_layers_cache[workspace] = (now + WFS_LAYERS_CACHE_TTL, result)
    return list(result)


def get_wfs_layer_text_fields(workspace: str, layer: str,
                              session: Optional[requests.Session] = None) -> List[str]:
    """
    Return the names of the text attributes of a layer (the fields a description can be searched in).

    - workspace: GeoServer workspace that owns the layer.
    - layer: Layer name without workspace prefix.
    - session: Optional requests session (defaults to the thread-local one).

    Raises GeoServerRequestError when GeoServer fails or its answer cannot be parsed.
    """
    resp = _wfs_get(
        workspace,
        {
            "request": "DescribeFeatureType",
            "typeNames": f"{workspace}:{layer}",
            "outputFormat": "application/json",
        },
        session,
    )

    try:
        feature_types = resp.json().get("featureTypes") or []
    except ValueError as e:
        logger.error("Invalid DescribeFeatureType answer for layer=%s: %s", layer, e)
        raise GeoServerRequestError(f"Invalid layer description returned by GeoServer: {e}")

    fields = []
    # A DescribeFeatureType answer has one entry per requested layer
    for feature_type in feature_types:
        # Check every attribute of the layer
        for prop in feature_type.get("properties") or []:
            # Keep only text attributes; numbers, dates and geometries are not searchable
            if prop.get("localType") == "string" and prop.get("name"):
                fields.append(prop["name"])
    return fields


def build_text_search_cql(fields: List[str], text: str) -> str:
    """
    Build a CQL filter that matches features whose text fields contain a text (case-insensitive).

    The text is escaped so it is always treated as a literal: quotes cannot close the
    string and the LIKE wildcards (% and _) lose their special meaning.

    - fields: Attribute names to search in.
    - text: Text to look for.

    Returns the CQL filter, e.g. "name" ILIKE '%cauca%' OR "code" ILIKE '%cauca%'.
    """
    # Escape the LIKE escape character first, then the wildcards and the quote
    escaped = (
        text.replace("\\", "\\\\")
        .replace("%", "\\%")
        .replace("_", "\\_")
        .replace("'", "''")
    )
    conditions = []
    # One ILIKE condition per text field, joined with OR
    for field in fields:
        quoted_field = field.replace('"', '""')
        conditions.append(f"\"{quoted_field}\" ILIKE '%{escaped}%'")
    return " OR ".join(conditions)


def get_wfs_features(workspace: str, layer: str, cql_filter: Optional[str] = None,
                     max_features: Optional[int] = None,
                     session: Optional[requests.Session] = None) -> Dict[str, Any]:
    """
    Get the features of a layer as a GeoJSON FeatureCollection in EPSG:4326 (lon/lat).

    - workspace: GeoServer workspace that owns the layer.
    - layer: Layer name without workspace prefix.
    - cql_filter: Optional CQL filter to select the features.
    - max_features: Optional maximum number of features to return.
    - session: Optional requests session (defaults to the thread-local one).

    Raises GeoServerRequestError when GeoServer fails or does not answer with GeoJSON.
    """
    params: Dict[str, Any] = {
        "request": "GetFeature",
        "typeNames": f"{workspace}:{layer}",
        "outputFormat": "application/json",
        "srsName": WFS_OUTPUT_CRS,
    }
    # Only send the filter when the caller wants a subset of the layer
    if cql_filter:
        params["cql_filter"] = cql_filter
    # Only limit the answer when a maximum was requested
    if max_features:
        params["count"] = max_features

    resp = _wfs_get(workspace, params, session)

    try:
        data = resp.json()
    except ValueError as e:
        # GeoServer reports WFS errors as XML with status 200, which is not valid JSON
        logger.error("GetFeature did not return GeoJSON for layer=%s: %s", layer, resp.text[:300])
        raise GeoServerRequestError(f"GeoServer did not return GeoJSON: {e}")
    return data

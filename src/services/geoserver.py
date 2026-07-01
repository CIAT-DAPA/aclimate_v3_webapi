"""
Shared GeoServer service module.

Centralizes:
- GeoServer connection configuration (URL, auth, HTTP session with connection pool)
- Date generation logic (daily/monthly/annual)
- WCS URL building
- Raster download with shared session
- Adaptive date limits based on temporality
- Structured logging
"""

import logging
import os
from datetime import date, timedelta
from typing import Dict, List, Literal, Optional, Tuple
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

# ---------- Constants ----------
# Maximum dates allowed per temporality (sync mode)
MAX_DATES_BY_TEMPORALITY: Dict[str, int] = {
    "daily": 7,
    "monthly": 12,
    "annual": 12,
}

DEFAULT_TIMEOUT = 60  # seconds


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
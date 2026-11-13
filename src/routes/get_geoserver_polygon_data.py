from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from typing import Any, Dict, List, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging
import zipstream
import rioxarray
from rasterio.io import MemoryFile
from rioxarray.exceptions import NoDataInBounds
from shapely.geometry import mapping, shape

from schemas.geoserver import PolygonDataRequest

from services.geoserver import (
    generate_date_list,
    get_geoserver_auth,
    get_geoserver_session,
    download_raster,
    MAX_WORKERS,
)

router = APIRouter(tags=["Geoserver"], prefix="/geoserver")

# ---------- Logger ----------
logger = logging.getLogger(__name__)

# ---------- Constants ----------
# CRS of the GeoJSON polygon (GeoJSON standard, RFC 7946)
POLYGON_CRS = "EPSG:4326"
# GeoJSON geometry types accepted to clip the rasters
POLYGON_GEOMETRY_TYPES = ("Polygon", "MultiPolygon")


def extract_polygon_geometries(geojson: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Extract and validate the polygon geometries contained in a GeoJSON object.

    - **geojson**: GeoJSON dict. It can be a Polygon/MultiPolygon geometry,
      a Feature or a FeatureCollection.

    Returns the list of GeoJSON geometries (Polygon/MultiPolygon) to clip with.
    Raises ValueError when the GeoJSON has no usable polygon geometry.
    """
    geojson_type = geojson.get("type")

    # Collect the raw geometries according to the GeoJSON object type
    if geojson_type == "FeatureCollection":
        # A FeatureCollection contributes the geometry of each of its features
        raw_geometries = [feature.get("geometry") for feature in geojson.get("features") or []]
    elif geojson_type == "Feature":
        # A Feature contributes its single geometry
        raw_geometries = [geojson.get("geometry")]
    elif geojson_type in POLYGON_GEOMETRY_TYPES:
        # A bare geometry is used as is
        raw_geometries = [geojson]
    else:
        raise ValueError(
            "polygon must be a GeoJSON Polygon, MultiPolygon, Feature or FeatureCollection"
        )

    geometries = []
    # Validate every geometry and keep only well-formed polygons
    for raw_geometry in raw_geometries:
        # Reject features without geometry or with non-polygon geometries (points, lines)
        if not raw_geometry or raw_geometry.get("type") not in POLYGON_GEOMETRY_TYPES:
            raise ValueError("all geometries in polygon must be of type Polygon or MultiPolygon")
        try:
            geometry = shape(raw_geometry)
        except Exception as e:
            raise ValueError(f"invalid polygon geometry: {e}")
        # Reject empty or topologically invalid polygons (e.g. self-intersections)
        if geometry.is_empty or not geometry.is_valid:
            raise ValueError("polygon geometry is empty or not valid")
        geometries.append(mapping(geometry))

    # At least one polygon is required to clip the rasters
    if not geometries:
        raise ValueError("polygon does not contain any geometry")

    return geometries


def clip_raster_bytes(raster_bytes: bytes, geometries: List[Dict[str, Any]]) -> Optional[bytes]:
    """
    Clip a GeoTIFF with the given polygon geometries.

    - **raster_bytes**: Content of the source GeoTIFF.
    - **geometries**: GeoJSON polygon geometries (EPSG:4326) used as the clip mask.

    Returns the clipped GeoTIFF content, or None when the polygons do not
    overlap the raster.
    """
    with MemoryFile(raster_bytes) as memfile:
        # Load the data in memory so it stays available after the file is closed
        xds = rioxarray.open_rasterio(memfile).load()

    # Rasters published without CRS are assumed to be in geographic coordinates
    if xds.rio.crs is None:
        xds = xds.rio.write_crs(POLYGON_CRS)

    try:
        # all_touched=True keeps every pixel touched by the polygon, so polygons
        # smaller than a pixel still return data. drop=True crops to the polygon extent.
        clipped = xds.rio.clip(geometries, crs=POLYGON_CRS, all_touched=True, drop=True)
    except NoDataInBounds:
        return None

    with MemoryFile() as mem_out:
        clipped.rio.to_raster(mem_out.name)
        return mem_out.read()


def process_polygon_date(date_info: Dict[str, str], geometries: List[Dict[str, Any]],
                         workspace: str, store: str) -> Tuple[str, Optional[bytes]]:
    """
    Download the raster of a specific date and clip it with the polygon.
    Uses the shared GeoServer session for connection pooling.

    - **date_info**: Dict with "date_str" and "time_subset" of the date to process.
    - **geometries**: GeoJSON polygon geometries (EPSG:4326) used as the clip mask.
    - **workspace**: Geoserver workspace.
    - **store**: Geoserver store/mosaic.

    Returns a tuple (date_str, clipped GeoTIFF bytes). The bytes are None when
    there is no raster for the date, the polygon is outside it or the clip fails.
    """
    date_str, time_subset = date_info["date_str"], date_info["time_subset"]

    # Use shared session for download
    session = get_geoserver_session()
    _, raster_bytes = download_raster(workspace, store, time_subset, session)

    # GeoServer has no raster for this date
    if raster_bytes is None:
        logger.warning("No data available for date %s", date_str)
        return date_str, None

    try:
        clipped_bytes = clip_raster_bytes(raster_bytes, geometries)
    except Exception as e:
        logger.error("Error clipping raster for %s: %s", date_str, e)
        return date_str, None

    # The polygon does not overlap the raster of this date
    if clipped_bytes is None:
        logger.warning("Polygon is outside the raster bounds for date %s", date_str)

    return date_str, clipped_bytes


@router.post(
    "/polygon-data",
    responses={
        200: {
            "description": "ZIP file with one clipped GeoTIFF per date ({date}.tif)",
            "content": {
                "application/zip": {
                    "schema": {"type": "string", "format": "binary"}
                }
            }
        },
        400: {
            "description": "Bad request - invalid GeoJSON polygon",
            "content": {
                "application/json": {
                    "example": {"detail": "Invalid polygon: polygon geometry is empty or not valid"}
                }
            }
        },
        404: {
            "description": "No data found for the given polygon and dates",
            "content": {
                "application/json": {
                    "example": {"detail": "No data found for the given polygon and dates"}
                }
            }
        }
    }
)
def get_polygon_data(
    request: PolygonDataRequest
):
    """
    Gets the rasters of a date range clipped by a polygon.

    Returns a ZIP file with one GeoTIFF per date (named `{date}.tif`), each one
    clipped to the polygon. Every pixel touched by the polygon is included.

    - **polygon**: GeoJSON with the polygon to cut data (Polygon, MultiPolygon, Feature or FeatureCollection in EPSG:4326)
    - **start_date**: Start date of the range
    - **end_date**: End date of the range
    - **workspace**: Geoserver workspace
    - **store**: Geoserver store/mosaic
    - **temporality**: Time frequency - "daily", "monthly", or "annual" (default: "daily")
    """
    try:
        # Validate credentials are configured
        get_geoserver_auth()

        # Validate the GeoJSON and get the polygon geometries used as clip mask
        try:
            geometries = extract_polygon_geometries(request.polygon)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=f"Invalid polygon: {str(e)}")

        # Generate date list using shared service
        start_date = request.start_date
        end_date = request.end_date if request.end_date else request.start_date
        dates_to_process = generate_date_list(start_date, end_date, request.temporality)

        # Process dates in parallel
        results = []
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            # Submit all tasks
            future_to_date = {
                executor.submit(
                    process_polygon_date,
                    date_info,
                    geometries,
                    request.workspace,
                    request.store,
                ): date_info for date_info in dates_to_process
            }

            # Collect results as they complete
            for future in as_completed(future_to_date):
                try:
                    date_str, data = future.result()
                except Exception as exc:
                    logger.error("Error processing date: %s", exc)
                    continue
                # Keep only the dates that produced a clipped raster
                if data is not None:
                    results.append((date_str, data))

        # No date had data inside the polygon
        if not results:
            raise HTTPException(status_code=404, detail="No data found for the given polygon and dates")

        # Sort results chronologically by date
        results.sort(key=lambda x: x[0])

        # Use no compression (ZIP_STORED) since GeoTIFFs are already compressed
        zip_stream = zipstream.ZipFile(mode='w', compression=zipstream.ZIP_STORED)
        # Add one GeoTIFF per date to the ZIP
        for date_str, data in results:
            zip_stream.writestr(f"{date_str}.tif", data)

        return StreamingResponse(
            zip_stream,
            media_type="application/zip",
            headers={"Content-Disposition": "attachment; filename=polygon_rasters.zip"},
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error processing polygon data request: %s", str(e))
        raise HTTPException(status_code=500, detail=f"Error processing data: {str(e)}")

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from typing import List, Optional, Dict
from datetime import date
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging
import zipstream
import rioxarray
from rasterio.io import MemoryFile

from aclimate_v3_cut_spatial_data import RioGeoServerClipper
from aclimate_v3_cut_spatial_data.types.geometry_types import GeoServerConnection

from schemas.geoserver import RasterExportRequest, ClipConfig

from services.geoserver import (
    generate_date_list,
    get_geoserver_auth,
    get_geoserver_url,
    get_geoserver_session,
    get_max_dates_for_temporality,
    download_raster,
    MAX_WORKERS,
)

router = APIRouter(tags=["Geoserver"], prefix="/geoserver")

# ---------- Logger ----------
logger = logging.getLogger(__name__)


# ---------- Funciones auxiliares ----------
def process_single_date(date_info: Dict, workspace: str, store: str,
                        clip_config: Optional[ClipConfig]) -> tuple:
    """Download a raster for a single date, optionally clip it, return (date_str, bytes)."""
    time_subset = date_info["time_subset"]
    date_str = date_info["date_str"]

    # Use shared session for download
    session = get_geoserver_session()
    _, raster_bytes = download_raster(workspace, store, time_subset, session)

    if raster_bytes is None:
        return date_str, None

    if clip_config and clip_config.enabled and clip_config.geoserver:
        try:
            with MemoryFile(raster_bytes) as memfile:
                xds = rioxarray.open_rasterio(memfile)
                if xds.rio.crs is None:
                    xds = xds.rio.write_crs("EPSG:4326")

            conn = GeoServerConnection(
                base_url=get_geoserver_url(),
                auth=get_geoserver_auth(),
            )
            clipper = RioGeoServerClipper(xds)
            clipper.connection = conn
            clipped = clipper.clip(
                workspace=clip_config.geoserver.workspace,
                layer=clip_config.geoserver.layer,
                cql_filter=clip_config.geoserver.cql_filter,
            )
            with MemoryFile() as mem_out:
                clipped.rio.to_raster(mem_out)
                raster_bytes = mem_out.read()
        except Exception as e:
            logger.warning("Clip failed for %s: %s", date_str, e)
            return date_str, None

    return date_str, raster_bytes


# ---------- Endpoint ----------
@router.post(
    "/raster-export",
    responses={
        200: {
            "description": "Successfully exported raster(s) as GeoTIFF or ZIP file",
            "content": {
                "image/tiff": {
                    "schema": {"type": "string", "format": "binary"},
                    "example": "single_tiff output returns a .tif file"
                },
                "application/zip": {
                    "schema": {"type": "string", "format": "binary"},
                    "example": "zip output returns a .zip file containing multiple .tif files"
                }
            }
        },
        400: {
            "description": "Bad request - too many dates requested or invalid parameters",
            "content": {
                "application/json": {
                    "example": {"detail": "Maximum 7 dates allowed for 'daily' temporality. Requested 10."}
                }
            }
        },
        404: {
            "description": "No data found for the given dates",
            "content": {
                "application/json": {
                    "example": {"detail": "No data found for the given dates"}
                }
            }
        }
    }
)
def export_rasters(request: RasterExportRequest):
    start = request.start_date
    end = request.end_date if request.end_date else start
    date_list = generate_date_list(start, end, request.temporality)

    # Validate date count against temporality-based limit
    max_dates = get_max_dates_for_temporality(request.temporality)
    if len(date_list) > max_dates:
        raise HTTPException(
            status_code=400,
            detail=f"Maximum {max_dates} dates allowed for '{request.temporality}' temporality. "
                   f"Requested {len(date_list)}.",
        )

    # Auth check (validates credentials are configured)
    get_geoserver_auth()

    results = []

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {
            executor.submit(
                process_single_date,
                d, request.workspace, request.store, request.clip
            ): d for d in date_list
        }
        for future in as_completed(futures):
            date_str, data = future.result()
            if data is not None:
                results.append((date_str, data))

    if not results:
        raise HTTPException(status_code=404, detail="No data found for the given dates")

    # Sort results chronologically by date string
    results.sort(key=lambda x: x[0])

    if len(results) == 1 and request.output_format == "single_tiff":
        date_str, data = results[0]
        return StreamingResponse(
            iter([data]),
            media_type="image/tiff",
            headers={"Content-Disposition": f'attachment; filename="{date_str}.tif"'},
        )
    else:
        # Use no compression (ZIP_STORED) since GeoTIFFs are already compressed
        zip_stream = zipstream.ZipFile(mode='w', compression=zipstream.ZIP_STORED)
        for date_str, data in results:
            zip_stream.writestr(f"{date_str}.tif", data)
        return StreamingResponse(
            zip_stream,
            media_type="application/zip",
            headers={"Content-Disposition": "attachment; filename=rasters.zip"},
        )
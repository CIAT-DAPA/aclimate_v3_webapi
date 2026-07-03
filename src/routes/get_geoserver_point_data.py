from fastapi import APIRouter, Query, HTTPException
from typing import List, Dict, Any
from datetime import date, timedelta
import requests
import numpy as np
import logging
from rasterio.io import MemoryFile
from concurrent.futures import ThreadPoolExecutor, as_completed

from schemas.geoserver import Coordinate, PointDataRequest, PointDataResult, PointDataResponse

from services.geoserver import (
    generate_date_list,
    get_geoserver_auth,
    get_geoserver_url,
    get_geoserver_session,
    download_raster,
    MAX_WORKERS,
)

router = APIRouter(tags=["Geoserver"], prefix="/geoserver")

# ---------- Logger ----------
logger = logging.getLogger(__name__)


def process_date_data(date_info: Dict, coordinates: List[List[float]],
                      workspace: str, store: str) -> List[PointDataResult]:
    """
    Process data for a specific date and return results for all coordinates.
    Uses the shared GeoServer session for connection pooling.
    """
    results = []
    current_date, date_str, time_subset = date_info['date'], date_info['date_str'], date_info['time_subset']

    # Use shared session for download
    session = get_geoserver_session()
    _, raster_bytes = download_raster(workspace, store, time_subset, session)

    if raster_bytes is None:
        logger.warning("No data available for date %s", date_str)
        return results

    try:
        # Process the raster and extract values for each coordinate
        with MemoryFile(raster_bytes) as memfile:
            with memfile.open() as raster:
                data_array = raster.read(1)

                for coord in coordinates:
                    lon, lat = coord[0], coord[1]

                    try:
                        # Check if coordinate is within bounds
                        if not (raster.bounds.left <= lon <= raster.bounds.right and
                                raster.bounds.bottom <= lat <= raster.bounds.top):
                            continue

                        # Get value from specific point
                        row, col = raster.index(lon, lat)

                        # Check if indices are within raster dimensions
                        if row < 0 or row >= raster.height or col < 0 or col >= raster.width:
                            continue

                        value = data_array[row, col]

                        # If the exact pixel is NaN, try nearby pixels
                        if np.isnan(value):
                            # Check 3x3 neighborhood
                            found_valid = False
                            for dr in [-1, 0, 1]:
                                for dc in [-1, 0, 1]:
                                    nr, nc = row + dr, col + dc
                                    if (0 <= nr < raster.height and 0 <= nc < raster.width):
                                        nearby_value = data_array[nr, nc]
                                        if not np.isnan(nearby_value) and nearby_value != -9999:
                                            value = nearby_value
                                            found_valid = True
                                            break
                                if found_valid:
                                    break

                        # Filter invalid values
                        if not np.isnan(value) and value != -9999 and (raster.nodata is None or value != raster.nodata):
                            results.append(PointDataResult(
                                coordinate=[lon, lat],
                                date=date_str,
                                value=float(value),
                            ))

                    except Exception:
                        continue

    except Exception as e:
        logger.error("Error processing raster for %s: %s", date_str, e)

    return results


@router.post("/point-data", response_model=PointDataResponse)
def get_point_data_from_coordinates(
    request: PointDataRequest
):
    """
    Gets point data from a raster for multiple coordinates within a date range.
    
    - **coordinates**: List of coordinates [[lon, lat], [lon, lat]]
    - **start_date**: Start date of the range
    - **end_date**: End date of the range  
    - **workspace**: Geoserver workspace
    - **store**: Geoserver store/mosaic
    - **temporality**: Time frequency - "daily", "monthly", or "annual" (default: "daily")
    """
    try:
        # Validate credentials are configured
        get_geoserver_auth()

        # Generate date list using shared service
        dates_to_process = []
        start_date = request.start_date
        end_date = request.end_date if request.end_date else request.start_date

        # Use the shared generate_date_list for consistency, then add 'date' field
        base_dates = generate_date_list(start_date, end_date, request.temporality)
        current_date = start_date
        for entry in base_dates:
            dates_to_process.append({
                'date': current_date,
                'date_str': entry['date_str'],
                'time_subset': entry['time_subset'],
            })
            # Advance the current_date for the 'date' field tracking
            if request.temporality == "daily":
                current_date += timedelta(days=1)
            elif request.temporality == "monthly":
                if current_date.month == 12:
                    current_date = current_date.replace(year=current_date.year + 1, month=1)
                else:
                    current_date = current_date.replace(month=current_date.month + 1)
            elif request.temporality == "annual":
                current_date = current_date.replace(year=current_date.year + 1)

        # Process dates in parallel
        all_results = []
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            # Submit all tasks
            future_to_date = {
                executor.submit(
                    process_date_data,
                    date_info,
                    request.coordinates,
                    request.workspace,
                    request.store,
                ): date_info for date_info in dates_to_process
            }

            # Collect results as they complete
            for future in as_completed(future_to_date):
                try:
                    results = future.result()
                    all_results.extend(results)
                except Exception as exc:
                    logger.error("Error processing date: %s", exc)
                    continue

        # Sort results chronologically by date
        all_results.sort(key=lambda x: x.date)

        return {
            "total_results": len(all_results),
            "data": all_results,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error processing point data request: %s", str(e))
        raise HTTPException(status_code=500, detail=f"Error processing data: {str(e)}")
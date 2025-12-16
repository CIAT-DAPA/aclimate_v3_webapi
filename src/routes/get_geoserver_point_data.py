from fastapi import APIRouter, Query, HTTPException, Depends
from typing import List, Dict, Any, Literal
from pydantic import BaseModel
from datetime import date, timedelta
import requests
import numpy as np
import os
from urllib.parse import urlencode
from rasterio.io import MemoryFile
from concurrent.futures import ThreadPoolExecutor, as_completed
from dependencies.auth_dependencies import get_current_user

router = APIRouter(tags=["Geoserver Point Data"], prefix="/geoserver")

class Coordinate(BaseModel):
    lon: float
    lat: float

class PointDataRequest(BaseModel):
    coordinates: List[List[float]]  # [[lon, lat], [lon, lat]]
    start_date: date
    end_date: date
    workspace: str
    store: str
    temporality: Literal["daily", "monthly", "annual"] = "daily"

class PointDataResult(BaseModel):
    coordinate: List[float]  # [lon, lat]
    date: str
    value: float

def process_date_data(date_info: Dict, coordinates: List[List[float]], auth: tuple, url_root: str, workspace: str, store: str) -> List[PointDataResult]:
    """
    Process data for a specific date and return results for all coordinates.
    """
    results = []
    current_date, date_str, time_subset = date_info['date'], date_info['date_str'], date_info['time_subset']
    
    # Build URL to get the raster
    base_url = f"{url_root}{workspace}/ows?"
    params = {
        "service": "WCS",
        "request": "GetCoverage", 
        "version": "2.0.1",
        "coverageId": store,
        "format": "image/geotiff",
        "subset": time_subset
    }
    url = base_url + urlencode(params)
    
    try:
        response = requests.get(url, auth=auth)
        
        if response.status_code == 404:
            # No data for this date
            return results
            
        response.raise_for_status()
        
        # Process the raster and extract values for each coordinate
        with MemoryFile(response.content) as memfile:
            with memfile.open() as raster:
                for coord in coordinates:
                    lon, lat = coord[0], coord[1]
                    
                    try:
                        # Get value from specific point
                        row, col = raster.index(lon, lat)
                        value = raster.read(1)[row, col]
                        
                        # Filter invalid values
                        if value != -9999 and not np.isnan(value):
                            results.append(PointDataResult(
                                coordinate=[lon, lat],
                                date=date_str,
                                value=float(value)
                            ))
                    except Exception:
                        # Coordinate outside raster bounds, continue
                        continue
                        
    except requests.exceptions.RequestException:
        # Error in request for this date
        pass
    
    return results

@router.post("/point-data")
def get_point_data_from_coordinates(
    request: PointDataRequest,
    current_user: dict = Depends(get_current_user)
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
        # Get credentials from environment variables
        geoserver_user = os.getenv('GEOSERVER_USER')
        geoserver_password = os.getenv('GEOSERVER_PASSWORD')
        
        if not geoserver_user or not geoserver_password:
            raise HTTPException(status_code=500, detail="Geoserver credentials not configured")
        
        # Get max workers from environment variable, default to 4
        max_workers = int(os.getenv('MAX_WORKERS', '4'))
        
        url_root = "https://geo.aclimate.org/geoserver/"
        auth = (geoserver_user, geoserver_password)
        
        # Generate all date information first
        dates_to_process = []
        current_date = request.start_date
        end_date = request.end_date
        
        while current_date <= end_date:
            year = current_date.year
            month = current_date.month
            day = current_date.day
            
            # Set time subset and date string based on temporality
            if request.temporality == "daily":
                time_subset = f"Time(\"{year:04d}-{month:02d}-{day:02d}T00:00:00.000Z\")"
                date_str = f"{year:04d}-{month:02d}-{day:02d}"
            elif request.temporality == "monthly":
                time_subset = f"Time(\"{year:04d}-{month:02d}-01T00:00:00.000Z\")"
                date_str = f"{year:04d}-{month:02d}-01"
            elif request.temporality == "annual":
                time_subset = f"Time(\"{year:04d}-01-01T00:00:00.000Z\")"
                date_str = f"{year:04d}-01-01"
            
            dates_to_process.append({
                'date': current_date,
                'date_str': date_str,
                'time_subset': time_subset
            })
            
            # Advance to next date based on temporality
            if request.temporality == "daily":
                current_date += timedelta(days=1)
            elif request.temporality == "monthly":
                if month == 12:
                    current_date = current_date.replace(year=year + 1, month=1)
                else:
                    current_date = current_date.replace(month=month + 1)
            elif request.temporality == "annual":
                current_date = current_date.replace(year=year + 1)
        
        # Process dates in parallel
        all_results = []
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all tasks
            future_to_date = {
                executor.submit(
                    process_date_data, 
                    date_info, 
                    request.coordinates, 
                    auth, 
                    url_root, 
                    request.workspace, 
                    request.store
                ): date_info for date_info in dates_to_process
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_date):
                try:
                    results = future.result()
                    all_results.extend(results)
                except Exception as exc:
                    # Log error but continue processing other dates
                    continue
        
        return {
            "request_parameters": {
                "coordinates": request.coordinates,
                "start_date": request.start_date.isoformat(),
                "end_date": request.end_date.isoformat(),
                "workspace": request.workspace,
                "store": request.store,
                "temporality": request.temporality,
            },
            "total_results": len(all_results),
            "data": all_results
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing data: {str(e)}")
from fastapi import APIRouter, Query
from aclimate_v3_orm.services.climate_historical_climatology_service import ClimateHistoricalClimatologyService
from aclimate_v3_orm.services.mng_location_service import MngLocationService
from typing import List

router = APIRouter(
    prefix="/climatology",
    tags=["Climate Historical Climatology"]
)

@router.get("/by-location-ids-date-range", response_model=List[dict])
def get_climatology_date_ranges_by_location_ids(
    location_ids: str = Query(..., description="Comma-separated location IDs")
):
    """
    Returns a list of locations with their ID, name, and the min and max month of climatology data.
    - **location_ids**: Comma-separated list of location IDs.
    """
    ids = [int(lid.strip()) for lid in location_ids.split(",")]
    
    climatology_service = ClimateHistoricalClimatologyService()
    location_service = MngLocationService()
    
    result = []
    
    for loc_id in ids:
        date_range = climatology_service.get_date_range_by_location_id(loc_id)
        
        if date_range["min_month"] is not None and date_range["max_month"] is not None:
            locations = location_service.get_all_enable()
            location = next((loc for loc in locations if loc.id == loc_id), None)
            
            if location:
                result.append({
                    "id": location.id,
                    "name": location.name,
                    "min_month": date_range["min_month"],
                    "max_month": date_range["max_month"]
                })
    
    return result

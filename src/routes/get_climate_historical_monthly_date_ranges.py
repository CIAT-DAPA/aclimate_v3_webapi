from fastapi import APIRouter, Query
from aclimate_v3_orm.services.climate_historical_monthly_service import ClimateHistoricalMonthlyService
from aclimate_v3_orm.services.mng_location_service import MngLocationService
from typing import List

router = APIRouter(
    prefix="/historical-monthly",
    tags=["Climate Historical Monthly"]
)

@router.get("/by-location-ids-date-range", response_model=List[dict])
def get_monthly_date_ranges_by_location_ids(
    location_ids: str = Query(..., description="Comma-separated location IDs")
):
    """
    Returns a list of locations with their ID, name, and the min and max date of climate monthly data.
    - **location_ids**: Comma-separated list of location IDs.
    """
    ids = [int(lid.strip()) for lid in location_ids.split(",")]
    
    monthly_service = ClimateHistoricalMonthlyService()
    location_service = MngLocationService()
    
    result = []
    
    for loc_id in ids:
        date_range = monthly_service.get_date_range_by_location_id(loc_id)
        
        if date_range["min_date"] is not None and date_range["max_date"] is not None:
            locations = location_service.get_all_enable()
            location = next((loc for loc in locations if loc.id == loc_id), None)
            
            if location:
                result.append({
                    "id": location.id,
                    "name": location.name,
                    "min_date": date_range["min_date"],
                    "max_date": date_range["max_date"]
                })
    
    return result

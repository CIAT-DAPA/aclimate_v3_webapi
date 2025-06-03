from fastapi import APIRouter, Query
from aclimate_v3_orm.services.climate_historical_daily_service import ClimateHistoricalDailyService
from aclimate_v3_orm.services.mng_location_service import MngLocationService
from typing import List

router = APIRouter(tags=["Climate Historical Daily"], prefix="/historical-daily")

@router.get("/by-location-ids-date-range", response_model=List[dict])
def get_date_ranges_by_location_ids(
    location_ids: str = Query(..., description="Comma-separated location IDs")
):
    """
    Return a list of locations with their ID, name, and the min and max date of climate data.
    - **location_ids**: Comma-separated list of location IDs.
    """
    ids = [int(lid.strip()) for lid in location_ids.split(",")]
    
    climate_service = ClimateHistoricalDailyService()
    location_service = MngLocationService()
    
    result = []
    
    for loc_id in ids:
        date_range = climate_service.get_date_range_by_location_id(loc_id)
        
        # Verificamos que min_date y max_date no sean None
        if date_range["min_date"] is not None and date_range["max_date"] is not None:
            # Consulta directa para obtener la ubicación por ID
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

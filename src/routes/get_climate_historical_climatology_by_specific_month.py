from fastapi import APIRouter, Query
from typing import List
from aclimate_v3_orm.services.climate_historical_climatology_service import ClimateHistoricalClimatologyService
from aclimate_v3_orm.schemas import ClimateHistoricalClimatologyRead

router = APIRouter(tags=["Climate Historical Climatology"], prefix="/climatology")

@router.get("/by-specific-month-location-ids-and-measures", response_model=List[dict])
def get_climatology_by_specific_month_location_ids_and_measures(
    location_ids: str = Query(..., description="Comma-separated location IDs, e.g. '1,2,3'"),
    measures: str = Query(..., description="Comma-separated measure short names, e.g. 'm1,m2'"),
    month: int = Query(..., description="Specific month (1-12)")
):
    """
    Returns climatology data for specific location IDs, measures, and a specific month.
    - **location_ids**: Comma-separated list of location IDs.
    - **measures**: Comma-separated list of measure short names.
    - **month**: Specific month (1-12).
    """
    service = ClimateHistoricalClimatologyService()
    ids = [int(lid.strip()) for lid in location_ids.split(",")]
    measure_short_names = [m.strip() for m in measures.split(",")]
    
    result = []
    for loc_id in ids:
        data = service.get_by_location_id(loc_id)
        filtered_data = [
            d for d in data if d.month == month and d.measure and d.measure.short_name in measure_short_names
        ]
        
        for d in filtered_data:
            simplified = {
                "id": d.id,
                "location_id": d.location_id,
                "location_name": d.location.name if d.location else None,
                "measure_id": d.measure_id,
                "measure_name": d.measure.name if d.measure else None,
                "measure_short_name": d.measure.short_name if d.measure else None,
                "measure_unit": d.measure.unit if d.measure else None,
                "month": d.month,
                "value": d.value
            }
            result.append(simplified)
    
    return result

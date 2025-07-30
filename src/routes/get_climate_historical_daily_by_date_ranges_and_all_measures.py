from fastapi import APIRouter, Query
from typing import List
from datetime import date
from aclimate_v3_orm.services import ClimateHistoricalDailyService
from aclimate_v3_orm.schemas import ClimateHistoricalDailyRead

router = APIRouter(tags=["Climate Historical Daily"], prefix="/historical-daily")

@router.get("/climate/by-date-range-all-measures", response_model=List[dict], summary="Get Climate Historical Daily Data by Date Range and All Measures")
def get_by_date_range_all_measures(
    location_ids: str = Query(..., description="Comma-separated location IDs, e.g. '1,2,3'"),
    start_date: date = Query(date(2025, 5, 1), description="Start date", examples="2025-05-01"),
    end_date: date = Query(date(2025, 5, 26), description="End date", examples="2025-05-26")
):
    """
    Returns simplified climate data for multiple location IDs and all measures within a date range.
    - **location_ids**: Comma-separated list of location IDs.
    - **start_date**: The start date for the range.
    - **end_date**: The end date for the range.
    """
    service = ClimateHistoricalDailyService()
    ids = [int(lid.strip()) for lid in location_ids.split(",")]
    
    result = []
    for loc_id in ids:
        data = service.get_by_location_id(loc_id)
        # Filtrar por fecha, pero sin filtro por measures
        filtered_data = [d for d in data if start_date <= d.date <= end_date]
        
        for d in filtered_data:
            simplified = {
                "id": d.id,
                "location_id": d.location_id,
                "location_name": d.location.name if d.location else None,
                "measure_id": d.measure_id,
                "measure_name": d.measure.name if d.measure else None,
                "measure_short_name": d.measure.short_name if d.measure else None,
                "measure_unit": d.measure.unit if d.measure else None,
                "date": d.date,
                "value": d.value,
                
            }
            result.append(simplified)
    
    return result

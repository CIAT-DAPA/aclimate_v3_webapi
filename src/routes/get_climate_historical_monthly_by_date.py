from fastapi import APIRouter, Query
from typing import List
from datetime import date
from aclimate_v3_orm.services import ClimateHistoricalMonthlyService
from aclimate_v3_orm.schemas import ClimateHistoricalMonthlyRead

router = APIRouter(tags=["Climate Historical Monthly"], prefix="/historical-monthly")

@router.get("/monthly/by-date", response_model=List[dict])
def get_by_date(
    location_ids: str = Query(..., description="Comma-separated location IDs, e.g. '1,2,3'"),
    measures: str = Query(..., description="Comma-separated measure short names, e.g. 'm1,m2'"),
    year: int = Query(2025, description="Year", example=2025),
    month: int = Query(5, description="Month", example=5)
):
    """
    Returns  monthly climate data for specific location IDs and measures for a specific year and month.
    - **location_ids**: Comma-separated list of location IDs.
    - **measures**: Comma-separated list of measure short names.
    - **year**: Year for the data.
    - **month**: Month for the data.
    """
    service = ClimateHistoricalMonthlyService()
    ids = [int(lid.strip()) for lid in location_ids.split(",")]
    measure_short_names = [m.strip() for m in measures.split(",")]
    
    target_date = date(year, month, 1)
    
    result = []
    for loc_id in ids:
        data = service.get_by_location_id(loc_id)
        filtered_data = [
            d for d in data 
            if d.date == target_date and d.measure and d.measure.short_name in measure_short_names
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
                "date": d.date,
                "value": d.value
            }
            result.append(simplified)
    
    return result

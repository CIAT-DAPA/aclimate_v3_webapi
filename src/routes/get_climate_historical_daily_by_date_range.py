from fastapi import APIRouter, Query
from typing import List, Optional
from datetime import date
from aclimate_v3_orm.services import ClimateHistoricalDailyService
from pydantic import BaseModel

router = APIRouter(tags=["Climate Historical Daily"], prefix="/historical-daily")

class ClimateHistoricalDaily(BaseModel):
    id: int
    location_id: int
    location_name: Optional[str]
    measure_id: Optional[int]
    measure_name: Optional[str]
    measure_short_name: Optional[str]
    measure_unit: Optional[str]
    date: date
    value: float

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "location_id": 123,
                "location_name": "Test Location",
                "measure_id": 5,
                "measure_name": "Precipitación",
                "measure_short_name": "m1",
                "measure_unit": "mm",
                "date": "2025-05-05",
                "value": 12.34
            }
        }

@router.get("/by-date-range", response_model=List[ClimateHistoricalDaily], summary="Get Climate Historical Daily Data by Date Range")
def get_by_date_range(
    location_ids: str = Query(..., description="Comma-separated location IDs, e.g. '1,2,3'"),
    start_date: date = Query(date(2025, 5, 1), description="Start date", examples="2025-05-01"),
    end_date: date = Query(date(2025, 5, 26), description="End date", examples="2025-05-26")
):
    """
    Returns  climate data for multiple location IDs within a date range.
    - **location_ids**: Comma-separated list of location IDs.
    - **start_date**: The start date for the range.
    - **end_date**: The end date for the range.
    """
    service = ClimateHistoricalDailyService()
    ids = [int(lid.strip()) for lid in location_ids.split(",")]
    
    result = []
    for loc_id in ids:
        data = service.get_by_location_id(loc_id)
        filtered_data = [d for d in data if start_date <= d.date <= end_date]
        
        for d in filtered_data:
            result.append({
                "id": d.id,
                "location_id": d.location_id,
                "location_name": d.location.name if d.location else None,
                "measure_id": d.measure_id,
                "measure_name": d.measure.name if d.measure else None,
                "measure_short_name": d.measure.short_name if d.measure else None,
                "measure_unit": d.measure.unit if d.measure else None,
                "date": d.date,
                "value": d.value
            })
    
    return result

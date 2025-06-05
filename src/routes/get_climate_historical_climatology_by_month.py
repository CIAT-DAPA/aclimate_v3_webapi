from fastapi import APIRouter, Query
from typing import List, Optional
from pydantic import BaseModel
from aclimate_v3_orm.services.climate_historical_climatology_service import ClimateHistoricalClimatologyService

router = APIRouter(tags=["Climate Historical Climatology"], prefix="/climatology")


class ClimateHistoricalClimatology(BaseModel):
    id: int
    location_id: int
    location_name: Optional[str]
    measure_id: Optional[int]
    measure_name: Optional[str]
    measure_short_name: Optional[str]
    measure_unit: Optional[str]
    month: int
    value: float

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "location_id": 456,
                "location_name": "Sample Location",
                "measure_id": 4,
                "measure_name": "Temperatura Máxima",
                "measure_short_name": "tmax",
                "measure_unit": "°C",
                "month": 5,
                "value": 32.7
            }
        }


@router.get(
    "/by-month-range-and-location-ids",
    response_model=List[ClimateHistoricalClimatology]
)
def get_climatology_by_month_range_and_location_ids(
    location_ids: str = Query(..., description="Comma-separated location IDs, e.g. '1,2,3'"),
    start_month: int = Query(..., description="Start month (1-12)"),
    end_month: int = Query(..., description="End month (1-12)")
):
    """
    Returns  climatology data for specific location IDs within a month range.
    - **location_ids**: Comma-separated list of location IDs.
    - **start_month**: Start month (1-12).
    - **end_month**: End month (1-12).
    """
    service = ClimateHistoricalClimatologyService()
    ids = [int(lid.strip()) for lid in location_ids.split(",")]
    
    result = []
    for loc_id in ids:
        data = service.get_by_location_id(loc_id)
        filtered_data = [d for d in data if start_month <= d.month <= end_month]
        
        for d in filtered_data:
            result.append({
                "id": d.id,
                "location_id": d.location_id,
                "location_name": d.location.name if d.location else None,
                "measure_id": d.measure_id,
                "measure_name": d.measure.name if d.measure else None,
                "measure_short_name": d.measure.short_name if d.measure else None,
                "measure_unit": d.measure.unit if d.measure else None,
                "month": d.month,
                "value": d.value
            })
    
    return result

from fastapi import APIRouter, Query
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
from aclimate_v3_orm.services.climate_historical_climatology_service import ClimateHistoricalClimatologyService

router = APIRouter(tags=["Climate Historical Climatology"], prefix="/climatology")

class MinMaxClimatologyRecord(BaseModel):
    measure_id: int
    measure_name: Optional[str] = None
    location_id: int
    location_name: Optional[str] = None
    min_value: float
    min_month: Optional[int] = None
    max_value: float
    max_month: Optional[int] = None

    class Config:
        json_schema_extra = {
            "example": {
                "measure_id": 2,
                "measure_name": "precipitation",
                "location_id": 10,
                "location_name": "Palmira",
                "min_value": 0.0,
                "min_month": "1",
                "max_value": 100.0,
                "max_month": "2"
            }
        }

@router.get("/minmax-by-location", response_model=List[MinMaxClimatologyRecord])
def minmax_climatology_by_location(location_id: int = Query(..., description="Location ID")):
    service = ClimateHistoricalClimatologyService()
    data = service.get_max_min_by_location_id(location_id)
    return [MinMaxClimatologyRecord(**d) for d in data]

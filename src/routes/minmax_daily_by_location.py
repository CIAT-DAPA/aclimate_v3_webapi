from fastapi import APIRouter, Query
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
from aclimate_v3_orm.services.climate_historical_daily_service import ClimateHistoricalDailyService

router = APIRouter(tags=["Climate Historical Daily"], prefix="/historical-daily")

class MinMaxDailyRecord(BaseModel):
    measure_id: int
    measure_name: Optional[str] = None
    location_id: int
    location_name: Optional[str] = None
    min_value: float
    min_date: Optional[datetime] = None
    max_value: float
    max_date: Optional[datetime] = None

    class Config:
        json_schema_extra = {
            "example": {
                "measure_id": 2,
                "measure_name": "precipitation",
                "location_id": 10,
                "location_name": "Palmira",
                "min_value": 0.0,
                "min_date": "2024-01-01T00:00:00Z",
                "max_value": 100.0,
                "max_date": "2024-01-31T00:00:00Z"
            }
        }

@router.get("/minmax-by-location", response_model=List[MinMaxDailyRecord])
def minmax_daily_by_location(location_id: int = Query(..., description="Location ID")):
    service = ClimateHistoricalDailyService()
    data = service.get_max_min_by_location_id(location_id)
    return [MinMaxDailyRecord(**d) for d in data]

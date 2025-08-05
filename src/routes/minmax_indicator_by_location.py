from fastapi import APIRouter, Query
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
from aclimate_v3_orm.services.climate_historical_indicator_service import ClimateHistoricalIndicatorService

router = APIRouter(tags=["Climate Historical Indicator"], prefix="/indicator")

class MinMaxIndicatorRecord(BaseModel):
    indicator_id: int
    indicator_name: Optional[str] = None
    location_id: int
    location_name: Optional[str] = None
    min_value: float
    min_date: Optional[datetime] = None
    max_value: float
    max_date: Optional[datetime] = None

    class Config:
        json_schema_extra = {
            "example": {
                "indicator_id": 2,
                "indicator_name": "consecutive_rainy_days",
                "location_id": 10,
                "location_name": "Palmira",
                "min_value": 1.0,
                "min_date": "2024-01-01T00:00:00Z",
                "max_value": 10.0,
                "max_date": "2024-01-31T00:00:00Z"
            }
        }

@router.get("/minmax-by-location", response_model=List[MinMaxIndicatorRecord])
def minmax_indicator_by_location(location_id: int = Query(..., description="Location ID")):
    service = ClimateHistoricalIndicatorService()
    data = service.get_max_min_by_location_id(location_id)
    result = []
    for d in data:
        mapped = d.copy()
        mapped["min_date"] = mapped.pop("min_start_date", None)
        mapped["max_date"] = mapped.pop("max_end_date", None)
        result.append(MinMaxIndicatorRecord(**mapped))
    return result

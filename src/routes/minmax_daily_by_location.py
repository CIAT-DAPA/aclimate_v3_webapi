from fastapi import APIRouter, Query
from typing import List
from aclimate_v3_orm.services.climate_historical_daily_service import ClimateHistoricalDailyService
from schemas.climate import MinMaxDailyRecord

router = APIRouter(tags=["Climate Historical Daily"], prefix="/historical-daily")

@router.get("/minmax-by-location", response_model=List[MinMaxDailyRecord])
def minmax_daily_by_location(location_id: int = Query(..., description="Location ID")):
    service = ClimateHistoricalDailyService()
    data = service.get_max_min_by_location_id(location_id)
    return [MinMaxDailyRecord(**d) for d in data]

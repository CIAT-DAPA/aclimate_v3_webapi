from fastapi import APIRouter, Query
from typing import List
from aclimate_v3_orm.services.climate_historical_monthly_service import ClimateHistoricalMonthlyService
from schemas.climate import MinMaxMonthlyRecord

router = APIRouter(tags=["Climate Historical Monthly"], prefix="/historical-monthly")

@router.get("/minmax-by-location", response_model=List[MinMaxMonthlyRecord])
def minmax_monthly_by_location(location_id: int = Query(..., description="Location ID")):
    service = ClimateHistoricalMonthlyService()
    data = service.get_max_min_by_location_id(location_id)
    return [MinMaxMonthlyRecord(**d) for d in data]

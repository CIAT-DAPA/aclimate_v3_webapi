from fastapi import APIRouter, Query
from typing import List
from aclimate_v3_orm.services.climate_historical_monthly_service import ClimateHistoricalMonthlyService
from schemas.climate import MinMaxDateRecord

router = APIRouter(tags=["Climate Historical Monthly"], prefix="/historical-monthly")

@router.get("/minmax-by-location", response_model=List[MinMaxDateRecord])
def minmax_monthly_by_location(location_id: int = Query(..., description="Location ID")):
    service = ClimateHistoricalMonthlyService()
    data = service.get_max_min_by_location_id(location_id)
    result = []
    for d in data:
        mapped = d.copy()
        mapped["id"] = mapped.pop("measure_id")
        mapped["name"] = mapped.pop("measure_name", None)
        result.append(MinMaxDateRecord(**mapped))
    return result

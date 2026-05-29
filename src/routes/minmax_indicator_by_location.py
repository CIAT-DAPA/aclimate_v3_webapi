from fastapi import APIRouter, Query
from typing import List
from aclimate_v3_orm.services.climate_historical_indicator_service import ClimateHistoricalIndicatorService
from schemas.climate import MinMaxDateRecord

router = APIRouter(tags=["Climate Historical Indicator"], prefix="/indicator")

@router.get("/minmax-by-location", response_model=List[MinMaxDateRecord])
def minmax_indicator_by_location(location_id: int = Query(..., description="Location ID")):
    service = ClimateHistoricalIndicatorService()
    data = service.get_max_min_by_location_id(location_id)
    result = []
    for d in data:
        mapped = d.copy()
        mapped["id"] = mapped.pop("indicator_id")
        mapped["name"] = mapped.pop("indicator_name", None)
        mapped["min_date"] = mapped.pop("min_start_date", None)
        mapped["max_date"] = mapped.pop("max_end_date", None)
        result.append(MinMaxDateRecord(**mapped))
    return result

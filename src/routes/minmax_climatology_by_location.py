from fastapi import APIRouter, Query
from typing import List
from aclimate_v3_orm.services.climate_historical_climatology_service import ClimateHistoricalClimatologyService
from schemas.climate import MinMaxClimatologyRecord

router = APIRouter(tags=["Climate Historical Climatology"], prefix="/climatology")

@router.get("/minmax-by-location", response_model=List[MinMaxClimatologyRecord])
def minmax_climatology_by_location(location_id: int = Query(..., description="Location ID")):
    service = ClimateHistoricalClimatologyService()
    data = service.get_max_min_by_location_id(location_id)
    return [MinMaxClimatologyRecord(**d) for d in data]

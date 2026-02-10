from fastapi import APIRouter, Query
from aclimate_v3_orm.services.mng_location_service import MngLocationService
from aclimate_v3_orm.services.climate_historical_daily_service import ClimateHistoricalDailyService
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from datetime import datetime

router = APIRouter(
    prefix="/locations",
    tags=["Locations"]
)


class MeasureData(BaseModel):
    """Climate measure data"""
    measure_id: int
    measure_name: str
    measure_short_name: str
    measure_unit: Optional[str]
    value: Optional[float]

    class Config:
        from_attributes = True


class LatestData(BaseModel):
    """Latest monitoring data for a location"""
    date: Optional[str]
    measures: List[MeasureData] = []

    class Config:
        from_attributes = True


class LocationWithData(BaseModel):
    """Location with its latest monitoring data"""
    id: int
    name: str
    ext_id: Optional[str]
    machine_name: Optional[str]
    enable: Optional[bool]
    altitude: Optional[float]
    latitude: Optional[float]
    longitude: Optional[float]
    visible: Optional[bool] = True
    source_id: Optional[int]
    source_name: Optional[str]
    source_type: Optional[str]
    admin2_id: Optional[int]
    admin2_name: Optional[str]
    admin2_ext_id: Optional[str]
    admin1_id: Optional[int]
    admin1_name: Optional[str]
    admin1_ext_id: Optional[str]
    country_id: int
    country_name: Optional[str]
    country_iso2: Optional[str]
    latest_data: Optional[LatestData]

    class Config:
        from_attributes = True


@router.get(
    "/by-country-ids-with-data",
    response_model=List[LocationWithData],
    summary="Get locations with latest monitoring data"
)
def get_locations_with_latest_data(
    country_ids: str = Query(..., description="Comma-separated country IDs, e.g. '1,2,3'"),
    days: int = Query(0, description="Number of days to look back for latest data (0 = no limit)", ge=0, le=365)
):
    """
    Return locations with their latest monitoring data in an optimized single response.
    
    - **country_ids**: Comma-separated list of country IDs
    - **days**: How many days back to search for data (0 = no limit, gets most recent available)
    """
    ids = [int(cid.strip()) for cid in country_ids.split(",")]
    
    location_service = MngLocationService()
    climate_service = ClimateHistoricalDailyService()
    result = []
    
    for country_id in ids:
        locations = location_service.get_by_country_id(country_id)
        
        for loc in locations:
            # Build base location object
            flat_loc = {
                "id": loc.id,
                "name": loc.name,
                "ext_id": loc.ext_id,
                "machine_name": loc.machine_name,
                "enable": loc.enable,
                "altitude": loc.altitude,
                "latitude": loc.latitude,
                "longitude": loc.longitude,
                "visible": loc.visible,
                "source_id": loc.source_id,
                "source_name": loc.source.name if loc.source else None,
                "source_type": loc.source.source_type if loc.source else None,
                "admin2_id": loc.admin_2.id if loc.admin_2 else None,
                "admin2_name": loc.admin_2.name if loc.admin_2 else None,
                "admin2_ext_id": loc.admin_2.ext_id if loc.admin_2 else None,
                "admin1_id": loc.admin_2.admin_1.id if loc.admin_2 and loc.admin_2.admin_1 else None,
                "admin1_name": loc.admin_2.admin_1.name if loc.admin_2 and loc.admin_2.admin_1 else None,
                "admin1_ext_id": loc.admin_2.admin_1.ext_id if loc.admin_2 and loc.admin_2.admin_1 and loc.admin_2.admin_1.ext_id else None,
                "country_id": loc.admin_2.admin_1.country.id if loc.admin_2 and loc.admin_2.admin_1 and loc.admin_2.admin_1.country else country_id,
                "country_name": loc.admin_2.admin_1.country.name if loc.admin_2 and loc.admin_2.admin_1 and loc.admin_2.admin_1.country else None,
                "country_iso2": loc.admin_2.admin_1.country.iso2 if loc.admin_2 and loc.admin_2.admin_1 and loc.admin_2.admin_1.country else None,
                "latest_data": None
            }
            
            # Try to get latest monitoring data
            try:
                latest_data = climate_service.get_latest_by_location(loc.id, days=days)
                if latest_data:
                    flat_loc["latest_data"] = {
                        "date": latest_data["date"].isoformat() if isinstance(latest_data["date"], datetime) else str(latest_data["date"]),
                        "measures": latest_data["measures"]
                    }
            except Exception as e:
                # Log error but continue - location is still valid without data
                print(f"Warning: Could not fetch data for location {loc.id}: {e}")
            
            result.append(flat_loc)
    
    return result

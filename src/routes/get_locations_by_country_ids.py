from fastapi import APIRouter, Query
from aclimate_v3_orm.services.mng_location_service import MngLocationService
from typing import List, Optional
from pydantic import BaseModel

router = APIRouter(
    prefix="/locations",
    tags=["Locations"]
)


class Location(BaseModel):
    id: int
    name: str
    ext_id: Optional[str]
    enable: Optional[bool]
    altitude: Optional[float]
    latitude: Optional[float]
    longitude: Optional[float]
    admin2_id: Optional[int]
    admin2_name: Optional[str]
    admin1_id: Optional[int]
    admin1_name: Optional[str]
    country_id: int
    country_name: Optional[str]
    country_iso2: Optional[str]

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 101,
                "name": "Test Location",
                "ext_id": "EXT101",
                "enable": True,
                "altitude": 2850.0,
                "latitude": -4.333,
                "longitude": -74.55,
                "admin2_id": 20,
                "admin2_name": "Bogotá",
                "admin1_id": 10,
                "admin1_name": "Cundinamarca",
                "country_id": 1,
                "country_name": "Colombia",
                "country_iso2": "CO"
            }
        }


@router.get("/by-country-ids", response_model=List[Location], summary="Get locations by country IDs")
def get_locations_by_country_ids(
    country_ids: str = Query(..., description="Comma-separated country IDs, e.g. '1,2,3'")
):
    """
    Return a flat list of locations for multiple country IDs with simplified fields.
    - **country_ids**: Comma-separated list of country IDs.
    """
    ids = [int(cid.strip()) for cid in country_ids.split(",")]
    
    service = MngLocationService()
    result = []
    
    for country_id in ids:
        locations = service.get_by_country_id(country_id)
        for loc in locations:
            flat_loc = {
                "id": loc.id,
                "name": loc.name,
                "ext_id": loc.ext_id,
                "enable": loc.enable,
                "altitude": loc.altitude,
                "latitude": loc.latitude,
                "longitude": loc.longitude,
                "admin2_id": loc.admin_2.id if loc.admin_2 else None,
                "admin2_name": loc.admin_2.name if loc.admin_2 else None,
                "admin1_id": loc.admin_2.admin_1.id if loc.admin_2 and loc.admin_2.admin_1 else None,
                "admin1_name": loc.admin_2.admin_1.name if loc.admin_2 and loc.admin_2.admin_1 else None,
                "country_id": loc.admin_2.admin_1.country.id if loc.admin_2 and loc.admin_2.admin_1 and loc.admin_2.admin_1.country else country_id,
                "country_name": loc.admin_2.admin_1.country.name if loc.admin_2 and loc.admin_2.admin_1 and loc.admin_2.admin_1.country else None,
                "country_iso2": loc.admin_2.admin_1.country.iso2 if loc.admin_2 and loc.admin_2.admin_1 and loc.admin_2.admin_1.country else None
            }
            result.append(flat_loc)
    
    return result

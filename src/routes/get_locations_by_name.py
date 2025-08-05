from fastapi import APIRouter, Query
from aclimate_v3_orm.services.mng_location_service import MngLocationService
from typing import List

router = APIRouter(
    prefix="/locations",
    tags=["Locations"]
)

@router.get("/by-name", response_model=List[dict])
def get_locations_by_name(
    name: str = Query(..., description="Location name")
):
    """
    Return a flat list of locations based on the provided name with simplified fields.
    - **name**: Name of the location(s) to search for.
    """
    service = MngLocationService()
    locations = service.get_by_name(name)
    
    result = []
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
            "country_id": loc.admin_2.admin_1.country.id if loc.admin_2 and loc.admin_2.admin_1 and loc.admin_2.admin_1.country else None,
            "country_name": loc.admin_2.admin_1.country.name if loc.admin_2 and loc.admin_2.admin_1 and loc.admin_2.admin_1.country else None,
            "country_iso2": loc.admin_2.admin_1.country.iso2 if loc.admin_2 and loc.admin_2.admin_1 and loc.admin_2.admin_1.country else None
        }
        result.append(flat_loc)
    
    return result

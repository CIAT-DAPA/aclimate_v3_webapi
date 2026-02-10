from fastapi import APIRouter, Query
from aclimate_v3_orm.services.mng_location_service import MngLocationService
from typing import List

router = APIRouter(
    prefix="/locations",
    tags=["Locations"]
)

@router.get("/by-id", response_model=List[dict])
def get_locations_by_id(
    id: int = Query(..., description="Location ID")
):
    """
    Return a location based on the provided ID with simplified fields.
    - **id**: ID of the location(s) to search for.
    """
    service = MngLocationService()
    location = service.get_by_id(id)
    result = []

    flat_loc = {
            "id": location.id,
            "name": location.name,
            "ext_id": location.ext_id,
            "machine_name": location.machine_name,
            "enable": location.enable,
            "altitude": location.altitude,
            "latitude": location.latitude,
            "longitude": location.longitude,
            "admin2_id": location.admin_2.id if location.admin_2 else None,
            "admin2_name": location.admin_2.name if location.admin_2 else None,
            "admin2_ext_id": location.admin_2.ext_id if location.admin_2 else None,
            "admin1_id": location.admin_2.admin_1.id if location.admin_2 and location.admin_2.admin_1 else None,
            "admin1_name": location.admin_2.admin_1.name if location.admin_2 and location.admin_2.admin_1 else None,
            "admin1_ext_id": location.admin_2.admin_1.ext_id if location.admin_2 and location.admin_2.admin_1 and location.admin_2.admin_1.ext_id else None,
            "country_id": location.admin_2.admin_1.country.id if location.admin_2 and location.admin_2.admin_1 and location.admin_2.admin_1.country else None,
            "country_name": location.admin_2.admin_1.country.name if location.admin_2 and location.admin_2.admin_1 and location.admin_2.admin_1.country else None,
            "country_iso2": location.admin_2.admin_1.country.iso2 if location.admin_2 and location.admin_2.admin_1 and location.admin_2.admin_1.country else None,
            "source": location.source.name if location.source else None
    }

    result.append(flat_loc)
    return result

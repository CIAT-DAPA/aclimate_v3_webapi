from fastapi import APIRouter, Query, HTTPException
from aclimate_v3_orm.services.mng_location_service import MngLocationService
from typing import List
from schemas.location import Location


router = APIRouter(
    prefix="/locations",
    tags=["Locations"]
)


def _build_location_response(loc) -> Location:
    """Helper function to build a Location response from LocationRead schema."""
    return Location(
        id=loc.id,
        name=loc.name,
        ext_id=loc.ext_id,
        machine_name=loc.machine_name,
        enable=loc.enable,
        altitude=loc.altitude,
        latitude=loc.latitude,
        longitude=loc.longitude,
        visible=loc.visible,
        admin2_id=loc.admin_2.id if loc.admin_2 else None,
        admin2_name=loc.admin_2.name if loc.admin_2 else None,
        admin2_ext_id=loc.admin_2.ext_id if loc.admin_2 else None,
        admin1_id=loc.admin_2.admin_1.id if loc.admin_2 and loc.admin_2.admin_1 else None,
        admin1_name=loc.admin_2.admin_1.name if loc.admin_2 and loc.admin_2.admin_1 else None,
        admin1_ext_id=loc.admin_2.admin_1.ext_id if loc.admin_2 and loc.admin_2.admin_1 else None,
        country_id=loc.admin_2.admin_1.country.id if loc.admin_2 and loc.admin_2.admin_1 and loc.admin_2.admin_1.country else None,
        country_name=loc.admin_2.admin_1.country.name if loc.admin_2 and loc.admin_2.admin_1 and loc.admin_2.admin_1.country else None,
        country_iso2=loc.admin_2.admin_1.country.iso2 if loc.admin_2 and loc.admin_2.admin_1 and loc.admin_2.admin_1.country else None,
        source=loc.source.name if loc.source else None
    )


@router.get("/search", response_model=List[Location])
def search_locations(
    q: str = Query(..., description="Text to search in location name, machine_name, ext_id, adm1, adm2 or country name")
):
    """
    Returns a list of locations based on a partial text search across
    location name, machine_name, ext_id, admin2 name, admin1 name and country name.
    - **q**: Text to search for.
    """
    service = MngLocationService()

    try:
        locations = service.search_by_name_machine_ext_id_and_hierarchy(q)
        return [_build_location_response(loc) for loc in locations]
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error searching locations: {str(e)}")
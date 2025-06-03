from fastapi import APIRouter, Query
from aclimate_v3_orm.services.mng_location_service import MngLocationService
from typing import List

router = APIRouter(
    prefix="/locations",
    tags=["Locations"]
)

@router.get("/by-country-ids", response_model=List[dict])
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
                "visible": loc.visible,
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

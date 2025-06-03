from fastapi import APIRouter, Depends, Query
from aclimate_v3_orm.services.mng_admin_2_service import MngAdmin2Service
from aclimate_v3_orm.schemas import Admin2Read
from dependencies.validate import get_current_user
from typing import List

router = APIRouter(
    prefix="/admin2",
    tags=["Admin levels"]
)

@router.get("/by-admin1-ids", response_model=List[dict])
def get_admin2_by_admin1_ids(
    admin1_ids: str = Query(..., description="Comma-separated admin1 IDs, e.g. '1,2,3'")
):
    """
    Return a flat list of admin2 for multiple admin1 IDs with simplified fields.
    - **admin1_ids**: Comma-separated list of admin1 IDs.
    """
    ids = [int(aid.strip()) for aid in admin1_ids.split(",")]
    
    service = MngAdmin2Service()
    result = []
    
    for admin1_id in ids:
        admin2_list = service.get_by_admin1_id(admin1_id)
        for admin2 in admin2_list:
            flat_admin2 = {
                "id": admin2.id,
                "name": admin2.name,
                "admin1_id": admin2.admin_1.id if admin2.admin_1 else admin1_id,  # fallback con admin1_id directo
                "admin1_name": admin2.admin_1.name if admin2.admin_1 else None,
                "country_id": admin2.admin_1.country.id if admin2.admin_1 and admin2.admin_1.country else None,
                "country_name": admin2.admin_1.country.name if admin2.admin_1 and admin2.admin_1.country else None,
                "country_iso2": admin2.admin_1.country.iso2 if admin2.admin_1 and admin2.admin_1.country else None
            }
            result.append(flat_admin2)
    
    return result

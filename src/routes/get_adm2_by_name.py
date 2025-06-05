from fastapi import APIRouter, Depends, Query
from aclimate_v3_orm.services.mng_admin_2_service import MngAdmin2Service
from aclimate_v3_orm.schemas import Admin2Read
from typing import List

router = APIRouter(
    prefix="/admin2",
    tags=["Admin levels"]
)

@router.get("/by-name", response_model=List[dict])
def get_admin2_by_name(
    name: str = Query(..., description="admin2 name")
):
    """
    Return a flat list of admin2 with simplified fields for the given name.
    - **name**: Name of the admin2 for which admin2 are being queried.
    """
    service = MngAdmin2Service()
    admin2_list = service.get_by_name(name)
    
    result = []
    for admin2 in admin2_list:
        flat_admin2 = {
            "id": admin2.id,
            "name": admin2.name,
            "admin1_id": admin2.admin_1.id if admin2.admin_1 else None,
            "admin1_name": admin2.admin_1.name if admin2.admin_1 else None,
            "country_id": admin2.admin_1.country.id if admin2.admin_1 and admin2.admin_1.country else None,
            "country_name": admin2.admin_1.country.name if admin2.admin_1 and admin2.admin_1.country else None,
            "country_iso2": admin2.admin_1.country.iso2 if admin2.admin_1 and admin2.admin_1.country else None
        }
        result.append(flat_admin2)
    
    return result

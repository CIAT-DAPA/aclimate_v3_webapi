from fastapi import APIRouter, Query
from aclimate_v3_orm.services.mng_admin_2_service import MngAdmin2Service
from typing import List
from schemas.location import Admin2

router = APIRouter(
    prefix="/admin2",
    tags=["Admin levels"]
)

@router.get("/by-name", response_model=List[Admin2])
def get_admin2_by_name(
    name: str = Query(..., description="admin2 name")
):
    """
    Return a list of admin2 with simplified fields for the given name.
    - **name**: Name of the admin2 for which admin2 are being queried.
    """
    service = MngAdmin2Service()
    admin2_list = service.get_by_name(name)

    return [
        Admin2(
            id=admin2.id,
            name=admin2.name,
            ext_id=admin2.ext_id,
            admin1_id=admin2.admin_1.id if admin2.admin_1 else None,
            admin1_name=admin2.admin_1.name if admin2.admin_1 else None,
            admin1_ext_id=admin2.admin_1.ext_id if admin2.admin_1 else None,
            country_id=admin2.admin_1.country.id if admin2.admin_1 and admin2.admin_1.country else None,
            country_name=admin2.admin_1.country.name if admin2.admin_1 and admin2.admin_1.country else None,
            country_iso2=admin2.admin_1.country.iso2 if admin2.admin_1 and admin2.admin_1.country else None
        )
        for admin2 in admin2_list
    ]

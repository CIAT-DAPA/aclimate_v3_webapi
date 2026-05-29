from fastapi import APIRouter, Query
from typing import List
from aclimate_v3_orm.services.mng_admin_1_service import MngAdmin1Service
from schemas.location import Admin1

router = APIRouter(
    prefix="/admin1",
    tags=["Admin levels"]
)



@router.get("/by-name", response_model=List[Admin1])
def get_admin1_by_name(
    name: str = Query(..., description="Name or partial name of the Admin1 region, case-insensitive")
):
    """
    Return a list of Admin1 regions that match a given name (case-insensitive, partial match).
    - **name**: Full or partial name to search for.
    """
    service = MngAdmin1Service()
    admin1_list = service.get_by_name(name)

    return [
        Admin1(
            id=adm.id,
            name=adm.name,
            ext_id=adm.ext_id,
            country_id=adm.country.id,
            country_name=adm.country.name,
            country_iso2=adm.country.iso2
        )
        for adm in admin1_list
    ]


# @router.get("/by-ext-id")
# def get_admin1_by_ext_id(
#     ext_id: str = Query(..., description="External ID of the Admin1 region")
# ):
#     """
#     Return an Admin1 region that matches a given external ID.
#     - **ext_id**: External ID to search for.
#     """
#     service = MngAdmin1Service()
#     admin1 = service.get_by_ext_id(ext_id)
#     
#     if admin1:
#         return {
#             "id": admin1.id,
#             "name": admin1.name,
#             "ext_id": admin1.ext_id,
#             "country_id": admin1.country.id,
#             "country_name": admin1.country.name,
#             "country_iso2": admin1.country.iso2
#         }
#     
#     return None

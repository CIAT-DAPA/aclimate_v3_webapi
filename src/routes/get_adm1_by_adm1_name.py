from fastapi import APIRouter, Query
from typing import List
from pydantic import BaseModel
from aclimate_v3_orm.services.mng_admin_1_service import MngAdmin1Service

router = APIRouter(
    prefix="/admin1",
    tags=["Admin levels"]
)



@router.get("/by-name")
def get_admin1_by_name(
    name: str = Query(..., description="Name or partial name of the Admin1 region, case-insensitive")
):
    """
    Return a list of Admin1 regions that match a given name (case-insensitive, partial match).
    - **name**: Full or partial name to search for.
    """
    service = MngAdmin1Service()
    all_admin1 = service.get_all()
    
    result = []
    for adm in all_admin1:
        if name.lower() in adm.name.lower():
            result.append({
                "id": adm.id,
                "name": adm.name,
                "country_id": adm.country.id,
                "country_name": adm.country.name,
                "country_iso2": adm.country.iso2
            })
    
    return result

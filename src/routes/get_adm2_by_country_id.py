from fastapi import APIRouter, Depends, Query
from aclimate_v3_orm.services.mng_admin_2_service import MngAdmin2Service
from typing import List
from pydantic import BaseModel

router = APIRouter(
    prefix="/admin2",
    tags=["Admin levels"]
)

class Admin2(BaseModel):
    id: int
    name: str
    ext_id: str
    admin1_id: int | None
    admin1_name: str | None
    admin1_ext_id: str | None
    country_id: int | None
    country_name: str | None
    country_iso2: str | None

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 302,
                "name": "Valle del Cauca",
                "ext_id": "76201",
                "admin1_id": 101,
                "admin1_name": "Pacífico",
                "admin1_ext_id": "76",
                "country_id": 1,
                "country_name": "Colombia",
                "country_iso2": "CO"
            }
        }

@router.get("/by-country-ids", response_model=List[Admin2])
def get_admin2_by_country_ids(
    country_ids: str = Query(..., description="Comma-separated country IDs, e.g. '1,2,3'")
):
    """
    Return a flat list of admin2 with simplified fields for multiple country IDs.
    - **country_ids**: Comma-separated list of country IDs.
    """
    ids = [int(cid.strip()) for cid in country_ids.split(",")]
    
    service = MngAdmin2Service()
    result = []
    
    for country_id in ids:
        admin2_list = service.get_by_country_id(country_id)
        for admin2 in admin2_list:
            flat_admin2 = {
                "id": admin2.id,
                "name": admin2.name,
                "ext_id": admin2.ext_id,
                "admin1_id": admin2.admin_1.id if admin2.admin_1 else None,
                "admin1_name": admin2.admin_1.name if admin2.admin_1 else None,
                "admin1_ext_id": admin2.admin_1.ext_id if admin2.admin_1 else None,
                "country_id": admin2.admin_1.country.id if admin2.admin_1 and admin2.admin_1.country else None,
                "country_name": admin2.admin_1.country.name if admin2.admin_1 and admin2.admin_1.country else None,
                "country_iso2": admin2.admin_1.country.iso2 if admin2.admin_1 and admin2.admin_1.country else None
            }
            result.append(flat_admin2)
    
    return result

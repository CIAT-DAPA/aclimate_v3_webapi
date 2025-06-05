from fastapi import APIRouter, Query
from typing import List, Optional
from pydantic import BaseModel
from aclimate_v3_orm.services.mng_admin_1_service import MngAdmin1Service

router = APIRouter(
    prefix="/admin1",
    tags=["Admin levels"]
)


class Admin1(BaseModel):
    id: int
    name: str
    country_id: int
    country_name: str
    country_iso2: str

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 101,
                "name": "Antioquia",
                "country_id": 1,
                "country_name": "Colombia",
                "country_iso2": "CO"
            }
        }


@router.get("/by-country-ids", response_model=List[Admin1])
def get_admin1_by_country_ids(
    country_ids: str = Query(..., description="Comma-separated country IDs, e.g. '1,2,3'")
):
    """
    Return a list of admin1 for multiple countries based on provided country IDs.
    - **country_ids**: Comma-separated list of country IDs.
    """
    ids = [int(cid.strip()) for cid in country_ids.split(",")]
    
    service = MngAdmin1Service()
    result = []
    
    for country_id in ids:
        admin1_list = service.get_by_country_id(country_id)
        for admin1 in admin1_list:
            result.append({
                "id": admin1.id,
                "name": admin1.name,
                "country_id": admin1.country.id,
                "country_name": admin1.country.name,
                "country_iso2": admin1.country.iso2
            })
    
    return result

from fastapi import APIRouter, Depends, Query
from dependencies.validate import get_current_user
from aclimate_v3_orm.services.mng_admin_1_service import MngAdmin1Service
from aclimate_v3_orm.schemas import Admin1Read
from typing import List

router = APIRouter(
    prefix="/admin1",
    tags=["Admin levels"]
)

@router.get("/by-country-ids", response_model=List[dict])  # Cambiado a List[dict]
def get_admin1_by_country_ids(
    country_ids: str = Query(..., description="Comma-separated country IDs, e.g. '1,2,3'")
):
    """
    Return a list of admin1 for multiple countries based on provided country IDs.
    - **country_ids**: Comma-separated list of country IDs.
    """
    # Convertir string a lista de enteros
    ids = [int(cid.strip()) for cid in country_ids.split(",")]
    
    service = MngAdmin1Service()
    
    result = []
    for country_id in ids:
        admin1_list = service.get_by_country_id(country_id)
        for admin1 in admin1_list:
            # Construir respuesta limpia
            clean_admin1 = {
                "id": admin1.id,
                "name": admin1.name,
                "country": {
                    "id": admin1.country.id,
                    "name": admin1.country.name,
                    "iso2": admin1.country.iso2
                }
            }
            result.append(clean_admin1)
    
    return result

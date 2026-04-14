from fastapi import APIRouter, Depends
from aclimate_v3_orm.services.mng_country_service import MngCountryService
from typing import List
from dependencies.auth_dependencies import get_current_user
from schemas.location import Country

router = APIRouter(tags=["Admin levels"])

country_service = MngCountryService()

@router.get("/countries", response_model=List[Country])
def get_all_countries(user: dict = Depends(get_current_user)):
    """
    Return a list of all enabled countries in the database with only id, name, and iso2.
    Requires a valid Keycloak token (user or client credentials).
    """
    countries = country_service.get_all_enable()
    simplified_countries = [
        {
            "id": country.id,
            "name": country.name,
            "iso2": country.iso2
        }
        for country in countries
    ]
    return simplified_countries

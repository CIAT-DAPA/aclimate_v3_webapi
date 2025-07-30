from fastapi import APIRouter, Depends, Query
from aclimate_v3_orm.services.mng_country_service import MngCountryService
from aclimate_v3_orm.schemas import CountryRead
from dependencies.auth_dependencies import get_current_user
from typing import List

router = APIRouter(tags=["Admin levels"])
country_service = MngCountryService()

@router.get("/countries/by-name", response_model=List[dict])  # Usar List[dict] para un filtrado dinámico
def get_countries_by_name(
    name: str = Query(
        "Colombia",  # Valor por defecto
        description="Country name",
        examples="Colombia"
    )
):
    """
    Return a list of countries based on the provided country name with only id, name, and iso2.
    - **name**: Name of the country for which countries are being queried.
    """
    countries = country_service.get_by_name(name)
    
    # Filtrar los campos a incluir (id, name, iso2)
    simplified_countries = [
        {
            "id": country.id,
            "name": country.name,
            "iso2": country.iso2
        }
        for country in countries
    ]
    
    return simplified_countries

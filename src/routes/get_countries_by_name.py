from fastapi import APIRouter, Query
from aclimate_v3_orm.services.mng_country_service import MngCountryService
from typing import List
from schemas.location import Country

router = APIRouter(tags=["Admin levels"])
country_service = MngCountryService()

@router.get("/countries/by-name", response_model=List[Country])
def get_countries_by_name(
    name: str = Query(
        "Colombia",
        description="Country name",
        examples="Colombia"
    )
):
    """
    Return a list of countries based on the provided country name with only id, name, and iso2.
    - **name**: Name of the country to search for.
    """
    countries = country_service.get_by_name(name)
    return [
        Country(
            id=country.id,
            name=country.name,
            iso2=country.iso2
        )
        for country in countries
    ]

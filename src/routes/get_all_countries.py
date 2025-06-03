from fastapi import APIRouter
from aclimate_v3_orm.services.mng_country_service import MngCountryService
from typing import List
from pydantic import BaseModel

router = APIRouter(tags=["Admin levels"])
country_service = MngCountryService()

class Country(BaseModel):
    id: int
    name: str
    iso2: str

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "name": "Colombia",
                "iso2": "CO"
            }
        }

@router.get("/countries", response_model=List[Country])
def get_all_countries():
    """
    Return a list of all enabled countries in the database with only id, name, and iso2.
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

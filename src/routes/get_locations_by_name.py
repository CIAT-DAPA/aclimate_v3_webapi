from fastapi import APIRouter, Query, HTTPException
from aclimate_v3_orm.services.mng_location_service import MngLocationService
from typing import List, Optional
from pydantic import BaseModel


class Location(BaseModel):
    id: int
    name: str
    ext_id: Optional[str] = None
    machine_name: Optional[str] = None
    enable: bool
    altitude: Optional[float] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    visible: bool
    admin2_id: Optional[int] = None
    admin2_name: Optional[str] = None
    admin2_ext_id: Optional[str] = None
    admin1_id: Optional[int] = None
    admin1_name: Optional[str] = None
    admin1_ext_id: Optional[str] = None
    country_id: Optional[int] = None
    country_name: Optional[str] = None
    country_iso2: Optional[str] = None

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "name": "Example Location",
                "ext_id": "EXT001",
                "machine_name": "example_location",
                "enable": True,
                "altitude": 1500.0,
                "latitude": 4.6097,
                "longitude": -74.0817,
                "visible": True,
                "admin2_id": 10,
                "admin2_name": "District Name",
                "admin2_ext_id": "DIST01",
                "admin1_id": 5,
                "admin1_name": "Region Name",
                "admin1_ext_id": "REG01",
                "country_id": 1,
                "country_name": "Colombia",
                "country_iso2": "CO"
            }
        }


router = APIRouter(
    prefix="/locations",
    tags=["Locations"]
)


def _build_location_response(loc) -> Location:
    """Helper function to build a Location response from LocationRead schema."""
    return Location(
        id=loc.id,
        name=loc.name,
        ext_id=loc.ext_id,
        machine_name=loc.machine_name,
        enable=loc.enable,
        altitude=loc.altitude,
        latitude=loc.latitude,
        longitude=loc.longitude,
        visible=loc.visible,
        admin2_id=loc.admin_2.id if loc.admin_2 else None,
        admin2_name=loc.admin_2.name if loc.admin_2 else None,
        admin2_ext_id=loc.admin_2.ext_id if loc.admin_2 else None,
        admin1_id=loc.admin_2.admin_1.id if loc.admin_2 and loc.admin_2.admin_1 else None,
        admin1_name=loc.admin_2.admin_1.name if loc.admin_2 and loc.admin_2.admin_1 else None,
        admin1_ext_id=loc.admin_2.admin_1.ext_id if loc.admin_2 and loc.admin_2.admin_1 else None,
        country_id=loc.admin_2.admin_1.country.id if loc.admin_2 and loc.admin_2.admin_1 and loc.admin_2.admin_1.country else None,
        country_name=loc.admin_2.admin_1.country.name if loc.admin_2 and loc.admin_2.admin_1 and loc.admin_2.admin_1.country else None,
        country_iso2=loc.admin_2.admin_1.country.iso2 if loc.admin_2 and loc.admin_2.admin_1 and loc.admin_2.admin_1.country else None
    )


@router.get("/by-name", response_model=List[Location])
def get_locations_by_name(
    name: str = Query(..., description="Location name")
):
    """
    Returns a list of locations based on the provided name with complete hierarchical data.
    - **name**: Name of the location(s) to search for.
    """
    service = MngLocationService()
    
    try:
        locations = service.get_by_name(name)
        return [_build_location_response(loc) for loc in locations]
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error fetching locations by name: {str(e)}")


@router.get("/by-machine-name", response_model=List[Location])
def get_locations_by_machine_name(
    machine_name: str = Query(..., description="Location machine name")
):
    """
    Returns a list of locations based on the provided machine name with complete hierarchical data.
    - **machine_name**: Machine name of the location(s) to search for.
    """
    service = MngLocationService()
    
    try:
        location = service.get_by_machine_name(machine_name)
        if not location:
            return []
        return [_build_location_response(location)]
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error fetching locations by machine name: {str(e)}")

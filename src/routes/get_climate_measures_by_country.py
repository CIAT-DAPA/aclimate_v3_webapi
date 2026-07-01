from fastapi import APIRouter, HTTPException
from typing import List
from aclimate_v3_orm.services.mng_country_climate_measure_service import MngCountryClimateMeasureService
from schemas.mng import ClimateMeasure

router = APIRouter(tags=["Country Climate Measures"], prefix="/countries")


@router.get("/{country_id}/climate-measures", response_model=List[ClimateMeasure])
def get_climate_measures_by_country(country_id: int):
    """
    Returns all climate measures (variables) configured for a specific country.

    - **country_id**: ID of the country (e.g., 1, 2, 3).
    """
    service = MngCountryClimateMeasureService()
    try:
        data = service.get_by_country(country_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error fetching climate measures by country: {str(e)}")

    if not data:
        return []

    return [
        ClimateMeasure(
            id=record.measure.id if record.measure else record.measure_id,
            name=record.measure.name if record.measure else None,
            short_name=record.measure.short_name if record.measure else None,
            unit=record.measure.unit if record.measure else None,
            description=record.measure.description if record.measure else None,
            enable=record.measure.enable if record.measure else None,
        )
        for record in data
    ]
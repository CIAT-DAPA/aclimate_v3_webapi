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

    # Filter only enabled measures and exclude enable field from response
    enabled_records = [
        record for record in data
        if record.measure and record.measure.enable
    ]

    return [
        ClimateMeasure(
            id=record.measure.id,
            name=record.measure.name,
            short_name=record.measure.short_name,
            unit=record.measure.unit,
            description=record.measure.description,
        )
        for record in enabled_records
    ]

from fastapi import APIRouter, HTTPException
from typing import List
from aclimate_v3_orm.services.mng_country_climate_measure_service import MngCountryClimateMeasureService
from schemas.mng import ClimateMeasure, CountryClimateMeasure

router = APIRouter(tags=["Country Climate Measures"], prefix="/countries")


def _serialize_temporality(temporality) -> List[str]:
    """Serialize Period enum values to lowercase strings."""
    if not temporality:
        return []
    return [t.value if hasattr(t, "value") else t for t in temporality]


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


@router.get("/{country_id}/climate-measures/configuration", response_model=List[CountryClimateMeasure])
def get_country_climate_measure_configuration(country_id: int):
    """
    Returns the country climate measure configuration for a specific country.

    Unlike /climate-measures (which returns the measure variable itself),
    this endpoint returns the full configuration (country_id, measure_id,
    spatial/location flags, temporality, description, store, workspace).

    - **country_id**: ID of the country (e.g., 1, 2, 3).
    """
    service = MngCountryClimateMeasureService()
    try:
        data = service.get_by_country(country_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error fetching country climate measure configuration: {str(e)}")

    if not data:
        return []

    # Filter only enabled measures
    enabled_records = [
        record for record in data
        if record.measure and record.measure.enable
    ]

    return [
        CountryClimateMeasure(
            id=record.id,
            country_id=record.country_id,
            measure_id=record.measure_id,
            spatial_forecast=record.spatial_forecast,
            spatial_climate=record.spatial_climate,
            location_forecast=record.location_forecast,
            location_climate=record.location_climate,
            temporality=_serialize_temporality(record.temporality),
            description=record.description,
            store=record.store,
            workspace=record.workspace,
        )
        for record in enabled_records
    ]

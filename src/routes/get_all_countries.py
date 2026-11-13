from fastapi import APIRouter, HTTPException
from aclimate_v3_orm.services.mng_country_service import MngCountryService
from aclimate_v3_orm.services.mng_country_climate_measure_service import MngCountryClimateMeasureService
from aclimate_v3_orm.services.mng_country_indicator_service import MngCountryIndicatorService
from typing import List
from schemas.location import Country, CountryClimateConf, CountryIndicatorConf
from routes.get_climate_measures_by_country import (
    _serialize_period,
    _serialize_location_climate_conf,
    _serialize_spatial_climate_conf,
)

router = APIRouter(tags=["Admin levels"])

country_service = MngCountryService()
country_climate_measure_service = MngCountryClimateMeasureService()
country_indicator_service = MngCountryIndicatorService()


def _build_conf_climate(country_id: int) -> List[CountryClimateConf]:
    """
    Build the climate configuration list of a country.

    Each item merges the country configuration (mng_country_climate_measure)
    with its measure (mng_climate_measure) in a single flat object without IDs.

    - **country_id**: ID of the country whose climate measures are requested.

    Returns the list of enabled climate measures configured for the country.
    """
    records = country_climate_measure_service.get_by_country(country_id)
    result = []
    # Go through every climate measure configured for the country
    for record in records:
        # Skip records without a measure or whose measure is disabled
        if not record.measure or not record.measure.enable:
            continue
        result.append(
            CountryClimateConf(
                name=record.measure.name,
                short_name=record.measure.short_name,
                unit=record.measure.unit,
                description=record.measure.description,
                country_description=record.description,
                spatial_forecast=record.spatial_forecast,
                spatial_climate=record.spatial_climate,
                location_forecast=record.location_forecast,
                location_climate=record.location_climate,
                spatial_climate_conf=_serialize_spatial_climate_conf(record.spatial_climate_conf),
                location_climate_conf=_serialize_location_climate_conf(record.location_climate_conf),
            )
        )
    return result


def _build_conf_indicator(country_id: int) -> List[CountryIndicatorConf]:
    """
    Build the indicator configuration list of a country.

    Each item merges the country configuration (mng_country_indicator) with its
    indicator (mng_indicators) and the indicator category (mng_indicator_category)
    in a single flat object without IDs.

    - **country_id**: ID of the country whose indicators are requested.

    Returns the list of enabled indicators configured for the country.
    """
    records = country_indicator_service.get_by_country(country_id)
    result = []
    # Go through every indicator configured for the country
    for record in records:
        indicator = record.indicator
        # Skip records without an indicator or whose indicator is disabled
        if not indicator or not indicator.enable:
            continue
        # The category is optional, so its fields fall back to None when missing
        category = getattr(indicator, "category", None)
        result.append(
            CountryIndicatorConf(
                type=_serialize_period(indicator.type),
                name=indicator.name,
                short_name=indicator.short_name,
                unit=indicator.unit,
                temporality=_serialize_period(indicator.temporality),
                description=indicator.description,
                category_name=category.name if category else None,
                category_description=category.description if category else None,
                country_description=record.description,
                spatial_forecast=record.spatial_forecast,
                spatial_climate=record.spatial_climate,
                location_forecast=record.location_forecast,
                location_climate=record.location_climate,
                criteria=record.criteria,
                store=record.store,
                workspace=record.workspace,
            )
        )
    return result


@router.get("/countries", response_model=List[Country])
def get_all_countries():
    """
    Return a list of all enabled countries in the database with id, name, iso2
    and their configuration:

    - **conf_climate**: climate measures configured for the country (measure data
      plus country flags and spatial/location configuration).
    - **conf_indicator**: indicators configured for the country (indicator and
      category data plus country flags, criteria, store and workspace).

    Only enabled measures and indicators are included and no IDs are exposed
    inside both lists.
    Requires a valid Keycloak token (user or client credentials).
    """
    try:
        countries = country_service.get_all_enable()
        result = []
        # Build the response of every enabled country with its configuration lists
        for country in countries:
            result.append(
                Country(
                    id=country.id,
                    name=country.name,
                    iso2=country.iso2,
                    conf_climate=_build_conf_climate(country.id),
                    conf_indicator=_build_conf_indicator(country.id),
                )
            )
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error fetching countries: {str(e)}")

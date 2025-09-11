from fastapi import APIRouter, Query, HTTPException
from typing import List, Optional, Dict
from pydantic import BaseModel
from aclimate_v3_orm.services.mng_country_indicator_service import MngCountryIndicatorService

class CountryIndicator(BaseModel):
    id: int
    country_id: int
    indicator_id: int
    spatial_forecast: bool
    spatial_climate: bool
    location_forecast: bool
    location_climate: bool
    criteria: Optional[Dict] = None

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "country_id": 1,
                "indicator_id": 2,
                "spatial_forecast": True,
                "spatial_climate": False,
                "location_forecast": True,
                "location_climate": True,
                "criteria": {"admin_level": 2, "threshold": 0.5}
            }
        }

router = APIRouter(tags=["Country Indicators"], prefix="/country-indicator")

@router.get("/by-country-id", response_model=List[CountryIndicator])
def get_by_country_id(
    country_id: int = Query(..., description="Country ID", ge=1)
):
    """
    Returns all indicators configured for a specific country.
    - **country_id**: ID of the country to filter indicators by (e.g., 1, 2, 3).
    """
    service = MngCountryIndicatorService()
    try:
        data = service.get_by_country(country_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error fetching indicators by country ID: {str(e)}")
    
    return [
        CountryIndicator(
            id=d.id,
            country_id=d.country_id,
            indicator_id=d.indicator_id,
            spatial_forecast=d.spatial_forecast,
            spatial_climate=d.spatial_climate,
            location_forecast=d.location_forecast,
            location_climate=d.location_climate,
            criteria=d.criteria
        ) for d in data
    ]

@router.get("/by-indicator-id", response_model=List[CountryIndicator])
def get_by_indicator_id(
    indicator_id: int = Query(..., description="Indicator ID", ge=1)
):
    """
    Returns all countries that have a specific indicator configured.
    - **indicator_id**: ID of the indicator to filter countries by (e.g., 1, 2, 3).
    """
    service = MngCountryIndicatorService()
    try:
        data = service.get_by_indicator(indicator_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error fetching countries by indicator ID: {str(e)}")
    
    return [
        CountryIndicator(
            id=d.id,
            country_id=d.country_id,
            indicator_id=d.indicator_id,
            spatial_forecast=d.spatial_forecast,
            spatial_climate=d.spatial_climate,
            location_forecast=d.location_forecast,
            location_climate=d.location_climate,
            criteria=d.criteria
        ) for d in data
    ]

@router.get("/by-country-and-indicator", response_model=CountryIndicator)
def get_by_country_and_indicator(
    country_id: int = Query(..., description="Country ID", ge=1),
    indicator_id: int = Query(..., description="Indicator ID", ge=1)
):
    """
    Returns the specific configuration of an indicator for a country.
    - **country_id**: ID of the country.
    - **indicator_id**: ID of the indicator.
    """
    service = MngCountryIndicatorService()
    try:
        data = service.get_by_country_and_indicator(country_id, indicator_id)
        if not data:
            raise HTTPException(status_code=404, detail=f"Configuration not found for country {country_id} and indicator {indicator_id}")
    except Exception as e:
        if "not found" in str(e).lower():
            raise HTTPException(status_code=404, detail=str(e))
        raise HTTPException(status_code=400, detail=f"Error fetching configuration: {str(e)}")
    
    return CountryIndicator(
        id=data.id,
        country_id=data.country_id,
        indicator_id=data.indicator_id,
        spatial_forecast=data.spatial_forecast,
        spatial_climate=data.spatial_climate,
        location_forecast=data.location_forecast,
        location_climate=data.location_climate,
        criteria=data.criteria
    )

@router.get("/spatial-forecast", response_model=List[CountryIndicator])
def get_spatial_forecast(
    country_id: int = Query(..., description="Country ID", ge=1)
):
    """
    Returns indicators configured for spatial forecast for a specific country.
    - **country_id**: ID of the country to filter indicators by.
    """
    service = MngCountryIndicatorService()
    try:
        data = service.get_by_country(country_id)
        # Filter by spatial_forecast = True
        filtered_data = [d for d in data if d.spatial_forecast]
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error fetching spatial forecast indicators: {str(e)}")
    
    return [
        CountryIndicator(
            id=d.id,
            country_id=d.country_id,
            indicator_id=d.indicator_id,
            spatial_forecast=d.spatial_forecast,
            spatial_climate=d.spatial_climate,
            location_forecast=d.location_forecast,
            location_climate=d.location_climate,
            criteria=d.criteria
        ) for d in filtered_data
    ]

@router.get("/spatial-climate", response_model=List[CountryIndicator])
def get_spatial_climate(
    country_id: int = Query(..., description="Country ID", ge=1)
):
    """
    Returns indicators configured for spatial climate for a specific country.
    - **country_id**: ID of the country to filter indicators by.
    """
    service = MngCountryIndicatorService()
    try:
        data = service.get_by_country(country_id)
        # Filter by spatial_climate = True
        filtered_data = [d for d in data if d.spatial_climate]
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error fetching spatial climate indicators: {str(e)}")
    
    return [
        CountryIndicator(
            id=d.id,
            country_id=d.country_id,
            indicator_id=d.indicator_id,
            spatial_forecast=d.spatial_forecast,
            spatial_climate=d.spatial_climate,
            location_forecast=d.location_forecast,
            location_climate=d.location_climate,
            criteria=d.criteria
        ) for d in filtered_data
    ]

@router.get("/location-forecast", response_model=List[CountryIndicator])
def get_location_forecast(
    country_id: int = Query(..., description="Country ID", ge=1)
):
    """
    Returns indicators configured for location forecast for a specific country.
    - **country_id**: ID of the country to filter indicators by.
    """
    service = MngCountryIndicatorService()
    try:
        data = service.get_by_country(country_id)
        # Filter by location_forecast = True
        filtered_data = [d for d in data if d.location_forecast]
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error fetching location forecast indicators: {str(e)}")
    
    return [
        CountryIndicator(
            id=d.id,
            country_id=d.country_id,
            indicator_id=d.indicator_id,
            spatial_forecast=d.spatial_forecast,
            spatial_climate=d.spatial_climate,
            location_forecast=d.location_forecast,
            location_climate=d.location_climate,
            criteria=d.criteria
        ) for d in filtered_data
    ]

@router.get("/location-climate", response_model=List[CountryIndicator])
def get_location_climate(
    country_id: int = Query(..., description="Country ID", ge=1)
):
    """
    Returns indicators configured for location climate for a specific country.
    - **country_id**: ID of the country to filter indicators by.
    """
    service = MngCountryIndicatorService()
    try:
        data = service.get_by_country(country_id)
        # Filter by location_climate = True
        filtered_data = [d for d in data if d.location_climate]
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error fetching location climate indicators: {str(e)}")
    
    return [
        CountryIndicator(
            id=d.id,
            country_id=d.country_id,
            indicator_id=d.indicator_id,
            spatial_forecast=d.spatial_forecast,
            spatial_climate=d.spatial_climate,
            location_forecast=d.location_forecast,
            location_climate=d.location_climate,
            criteria=d.criteria
        ) for d in filtered_data
    ]
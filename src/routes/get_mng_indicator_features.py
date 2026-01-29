from fastapi import APIRouter, Query, HTTPException
from typing import List, Optional
from pydantic import BaseModel
from aclimate_v3_orm.services.mng_indicators_features_service import MngIndicatorsFeaturesService
from aclimate_v3_orm.services.mng_country_indicator_service import MngCountryIndicatorService


class IndicatorFeature(BaseModel):
    id: int
    country_indicator_id: int
    title: str
    description: Optional[str] = None
    type: str

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "country_indicator_id": 1,
                "title": "Temperature Management",
                "description": "Best practices for managing temperature stress",
                "type": "recommendation"
            }
        }


router = APIRouter(tags=["Indicator Features"], prefix="/indicator-features")


@router.get("/by-id", response_model=IndicatorFeature)
def get_by_id(
    id: int = Query(..., description="Indicator feature ID", ge=1)
):
    """
    Returns an indicator feature filtered by ID.
    - **id**: ID of the indicator feature to retrieve.
    """
    service = MngIndicatorsFeaturesService()
    
    try:
        data = service.get_by_id(id)
        if not data:
            raise HTTPException(status_code=404, detail=f"Indicator feature with ID {id} not found")
        
        return IndicatorFeature(
            id=data.id,
            country_indicator_id=data.country_indicator_id,
            title=data.title,
            description=data.description,
            type=data.type
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error fetching indicator feature by ID: {str(e)}")


@router.get("/by-type", response_model=List[IndicatorFeature])
def get_by_type(
    type: str = Query(..., description="Feature type (recommendation or feature)")
):
    """
    Returns all indicator features filtered by type.
    - **type**: Type of the feature (e.g., 'recommendation', 'feature').
    """
    service = MngIndicatorsFeaturesService()
    
    try:
        data = service.get_by_type(type.lower())
        return [
            IndicatorFeature(
                id=d.id,
                country_indicator_id=d.country_indicator_id,
                title=d.title,
                description=d.description,
                type=d.type
            ) for d in data
        ]
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error fetching indicator features by type: {str(e)}")


@router.get("/by-country-indicator", response_model=List[IndicatorFeature])
def get_by_country_indicator(
    country_indicator_id: int = Query(..., description="Country indicator ID", ge=1)
):
    """
    Returns all features for a given country indicator.
    - **country_indicator_id**: ID of the country indicator.
    """
    service = MngIndicatorsFeaturesService()
    
    try:
        data = service.get_by_country_indicator(country_indicator_id)
        return [
            IndicatorFeature(
                id=d.id,
                country_indicator_id=d.country_indicator_id,
                title=d.title,
                description=d.description,
                type=d.type
            ) for d in data
        ]
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error fetching indicator features by country indicator: {str(e)}")


@router.get("/by-country-indicator-and-type", response_model=List[IndicatorFeature])
def get_by_country_indicator_and_type(
    country_indicator_id: int = Query(..., description="Country indicator ID", ge=1),
    type: str = Query(..., description="Feature type (recommendation or feature)")
):
    """
    Returns features for a given country indicator filtered by type.
    - **country_indicator_id**: ID of the country indicator.
    - **type**: Type of the feature (e.g., 'recommendation', 'feature').
    """
    service = MngIndicatorsFeaturesService()
    
    try:
        data = service.get_by_country_indicator_and_type(country_indicator_id, type.lower())
        return [
            IndicatorFeature(
                id=d.id,
                country_indicator_id=d.country_indicator_id,
                title=d.title,
                description=d.description,
                type=d.type
            ) for d in data
        ]
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error fetching indicator features: {str(e)}")


@router.get("/by-indicator-and-country", response_model=List[IndicatorFeature])
def get_by_indicator_and_country(
    indicator_id: int = Query(..., description="Indicator ID", ge=1),
    country_id: int = Query(..., description="Country ID", ge=1),
    type: Optional[str] = Query(None, description="Feature type filter (recommendation or feature)")
):
    """
    Returns features for a specific indicator in a specific country.
    - **indicator_id**: ID of the indicator.
    - **country_id**: ID of the country.
    - **type**: Optional type filter (e.g., 'recommendation', 'feature').
    """
    try:
        # Get the country_indicator for this indicator and country
        country_indicator_service = MngCountryIndicatorService()
        country_indicator = country_indicator_service.get_by_country_and_indicator(country_id, indicator_id)
        
        if not country_indicator:
            raise HTTPException(
                status_code=404, 
                detail=f"Indicator {indicator_id} not found for country {country_id}"
            )
        
        # Get features for this country_indicator
        features_service = MngIndicatorsFeaturesService()
        
        if type:
            data = features_service.get_by_country_indicator_and_type(country_indicator.id, type.lower())
        else:
            data = features_service.get_by_country_indicator(country_indicator.id)
        
        return [
            IndicatorFeature(
                id=d.id,
                country_indicator_id=d.country_indicator_id,
                title=d.title,
                description=d.description,
                type=d.type
            ) for d in data
        ]
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error fetching indicator features: {str(e)}")

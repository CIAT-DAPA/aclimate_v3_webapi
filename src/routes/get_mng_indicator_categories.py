from fastapi import APIRouter, Query, HTTPException, Depends, Path
from typing import List, Optional
from pydantic import BaseModel
from aclimate_v3_orm.services.mng_indicator_category_service import MngIndicatorCategoryService
from aclimate_v3_orm.services.mng_country_indicator_service import MngCountryIndicatorService
from aclimate_v3_orm.services.mng_indicators_service import MngIndicatorService

from datetime import datetime

class IndicatorCategory(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    enable: bool
    registered_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "name": "Climate",
                "description": "Climate-related indicators",
                "enable": True,
                "registered_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-02T00:00:00Z"
            }
        }

router = APIRouter(tags=["Indicator Categories"], prefix="/indicator-category-mng")

@router.get("/by-name", response_model=IndicatorCategory)
def get_by_name(
    name: str = Query(..., description="Category name")
):
    """
    Returns category filtered by exact name.
    - **name**: Name of the category to filter by (e.g., 'Extreme Temperature', 'Heat Stress').
    """
    service = MngIndicatorCategoryService()
    data = service.get_by_name(name)
    if not data:
        raise HTTPException(status_code=404, detail=f"Category with name '{name}' not found")
    
    return IndicatorCategory(
        id=data.id,
        name=data.name,
        description=data.description,
        enable=data.enable,
        registered_at=data.registered_at,
        updated_at=data.updated_at
    )

@router.get("/all", response_model=List[IndicatorCategory])
def get_all():
    """
    Returns all indicator categories.
    """
    service = MngIndicatorCategoryService()
    data = service.get_all()
    return [
        IndicatorCategory(
            id=d.id,
            name=d.name,
            description=d.description,
            enable=d.enable,
            registered_at=d.registered_at,
            updated_at=d.updated_at
        ) for d in data
    ]


@router.get("/by-category", response_model=IndicatorCategory)
def get_by_category_id(
    category_id: int = Query(..., description="Category ID", ge=1)
):
    """
    Returns category by ID.
    - **category_id**: ID of the category to retrieve (e.g., 1, 2, 3).
    Use: /by-category?category_id=1
    """
    service = MngIndicatorCategoryService()
    try:
        data = service.get_by_id(category_id)
        if not data:
            raise HTTPException(status_code=404, detail=f"Category with ID {category_id} not found")
        
        return IndicatorCategory(
            id=data.id,
            name=data.name,
            description=data.description,
            enable=data.enable,
            registered_at=data.registered_at,
            updated_at=data.updated_at
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error fetching category by ID: {str(e)}")

@router.get("/by-country", response_model=List[IndicatorCategory])
def get_by_country(
    country_id: int = Query(..., description="Country ID")
):
    """
    Returns unique indicator categories for a given country.
    - **country_id**: ID of the country to get categories for (e.g., 1, 2, 3).
    """
    try:
        # Get indicators by country using MngCountryIndicatorService
        country_indicator_service = MngCountryIndicatorService()
        country_indicators = country_indicator_service.get_by_country(country_id)
        if not country_indicators:
            return []
        
        # Extract indicator IDs from country indicators
        indicator_ids = [ci.indicator_id for ci in country_indicators]
        
        # Get full indicator details using MngIndicatorService
        indicator_service = MngIndicatorService()
        
        # Get all indicators for this country and extract unique category IDs
        category_ids = set()
        for indicator_id in indicator_ids:
            indicator_data = indicator_service.get_by_id(indicator_id)
            if indicator_data and indicator_data.enable:  # Only consider enabled indicators
                category_ids.add(indicator_data.indicator_category_id)
        
        # Get full category details using MngIndicatorCategoryService
        category_service = MngIndicatorCategoryService()
        categories = []
        
        for category_id in category_ids:
            category_data = category_service.get_by_id(category_id)
            if category_data and category_data.enable:  # Only include enabled categories
                categories.append(IndicatorCategory(
                    id=category_data.id,
                    name=category_data.name,
                    description=category_data.description,
                    enable=category_data.enable,
                    registered_at=category_data.registered_at,
                    updated_at=category_data.updated_at
                ))
        
        # Sort categories by ID for consistent ordering
        categories.sort(key=lambda x: x.id)
        
        return categories
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error fetching categories by country: {str(e)}")
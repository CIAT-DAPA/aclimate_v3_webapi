from fastapi import APIRouter, Query, HTTPException, Depends, Path
from typing import List, Optional
from pydantic import BaseModel
from aclimate_v3_orm.services.mng_indicator_category_service import MngIndicatorCategoryService

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
    - **name**: Name of the category to filter by (e.g., 'Climate', 'Agroclimatic').
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


@router.get("/{category_id}", response_model=IndicatorCategory)
def get_by_id(
    category_id: int = Path(..., description="Category ID", ge=1)
):
    """
    Returns category by ID.
    - **category_id**: ID of the category to retrieve (e.g., 1, 2, 3).
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
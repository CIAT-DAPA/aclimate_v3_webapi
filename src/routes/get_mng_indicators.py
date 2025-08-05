
from fastapi import APIRouter, Query, HTTPException, Depends
from typing import List, Optional
from pydantic import BaseModel
from aclimate_v3_orm.services.mng_indicators_service import MngIndicatorService

from datetime import datetime

class Indicator(BaseModel):
    id: int
    name: str
    short_name: str
    unit: str
    type: str
    description: Optional[str] = None
    enable: bool
    registered_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "name": "consecutive_rainy_days",
                "short_name": "crd",
                "unit": "days",
                "type": "CLIMATE",
                "description": "Consecutive rainy days indicator",
                "enable": True,
                "registered_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-02T00:00:00Z"
            }
        }
router = APIRouter(tags=["Indicators"], prefix="/indicator-mng")

@router.get("/by-name", response_model=List[Indicator])
def get_by_name(
    name: str = Query(..., description="Indicator name")
):
    """
    Returns indicators filtered by exact name.
    - **name**: Name of the indicator to filter by (e.g., 'consecutive_rainy_days').
    """
    service = MngIndicatorService()
    data = service.get_by_name(name)
    return [
        Indicator(
            id=d.id,
            name=d.name,
            short_name=d.short_name,
            unit=d.unit,
            type=d.type,
            description=d.description,
            enable=d.enable,
            registered_at=d.registered_at,
            updated_at=d.updated_at
        ) for d in data
    ]

@router.get("/by-short-name", response_model=List[Indicator])
def get_by_short_name(
    short_name: str = Query(..., description="Indicator short name")
):
    """
    Returns indicators filtered by exact short name.
    - **short_name**: Short name of the indicator to filter by (e.g., 'crd').
    """
    service = MngIndicatorService()
    data = service.get_by_short_name(short_name)
    return [
        Indicator(
            id=d.id,
            name=d.name,
            short_name=d.short_name,
            unit=d.unit,
            type=d.type,
            description=d.description,
            enable=d.enable,
            registered_at=d.registered_at,
            updated_at=d.updated_at
        ) for d in data
    ]

@router.get("/by-type", response_model=List[Indicator])
def get_by_type(
    type: str = Query(..., description="Indicator type")
):
    """
    Returns indicators filtered by type.
    - **type**: Type of the indicator to filter by (e.g., 'CLIMATE', 'AGROCLIMATIC').
    """
    service = MngIndicatorService()
    type_upper = type.upper()
    try:
        data = service.get_by_type(type_upper)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid indicator type: {type}")
    return [
        Indicator(
            id=d.id,
            name=d.name,
            short_name=d.short_name,
            unit=d.unit,
            type=d.type,
            description=d.description,
            enable=d.enable,
            registered_at=d.registered_at,
            updated_at=d.updated_at
        ) for d in data
    ]

@router.get("/all-enabled", response_model=List[Indicator])
def get_all_enabled():
    """
    Returns all enabled indicators.
    """
    service = MngIndicatorService()
    data = service.get_all_enabled()
    return [
        Indicator(
            id=d.id,
            name=d.name,
            short_name=d.short_name,
            unit=d.unit,
            type=d.type,
            description=d.description,
            enable=d.enable,
            registered_at=d.registered_at,
            updated_at=d.updated_at
        ) for d in data
    ]

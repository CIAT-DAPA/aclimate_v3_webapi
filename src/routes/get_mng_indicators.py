from fastapi import APIRouter, Query, HTTPException
from typing import List
from aclimate_v3_orm.services.mng_indicators_service import MngIndicatorService

router = APIRouter(tags=["Indicators"], prefix="/indicator-mng")

@router.get("/by-name", response_model=List[dict])
def get_by_name(
    name: str = Query(..., description="Indicator name")
):
    """
    Returns indicators filtered by exact name.
    - **name**: Name of the indicator to filter by (e.g., 'consecutive_rainy_days').
    """
    service = MngIndicatorService()
    data = service.get_by_name(name)
    result = [
        {
            "id": d.id,
            "name": d.name,
            "short_name": d.short_name,
            "unit": d.unit,
            "type": d.type,
            "description": d.description,
            "enable": d.enable,
            "registered_at": d.registered_at,
            "updated_at": d.updated_at
        }
        for d in data
    ]
    return result

@router.get("/by-short-name", response_model=List[dict])
def get_by_short_name(
    short_name: str = Query(..., description="Indicator short name")
):
    """
    Returns indicators filtered by exact short name.
    - **short_name**: Short name of the indicator to filter by (e.g., 'crd').
    """
    service = MngIndicatorService()
    data = service.get_by_short_name(short_name)
    result = [
        {
            "id": d.id,
            "name": d.name,
            "short_name": d.short_name,
            "unit": d.unit,
            "type": d.type,
            "description": d.description,
            "enable": d.enable,
            "registered_at": d.registered_at,
            "updated_at": d.updated_at
        }
        for d in data
    ]
    return result

@router.get("/by-type", response_model=List[dict])
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
    result = [
        {
            "id": d.id,
            "name": d.name,
            "short_name": d.short_name,
            "unit": d.unit,
            "type": d.type,
            "description": d.description,
            "enable": d.enable,
            "registered_at": d.registered_at,
            "updated_at": d.updated_at
        }
        for d in data
    ]
    return result

@router.get("/all-enabled", response_model=List[dict])
def get_all_enabled():
    """
    Returns all enabled indicators.
    """
    service = MngIndicatorService()
    data = service.get_all_enabled()
    result = [
        {
            "id": d.id,
            "name": d.name,
            "short_name": d.short_name,
            "unit": d.unit,
            "type": d.type,
            "description": d.description,
            "enable": d.enable,
            "registered_at": d.registered_at,
            "updated_at": d.updated_at
        }
        for d in data
    ]
    return result

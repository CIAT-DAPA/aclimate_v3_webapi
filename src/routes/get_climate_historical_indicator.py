
from fastapi import APIRouter, Query, HTTPException
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
from aclimate_v3_orm.services.climate_historical_indicator_service import ClimateHistoricalIndicatorService

class ClimateHistoricalIndicatorRecord(BaseModel):
    id: int
    indicator_id: int
    indicator_name: Optional[str] = None
    indicator_short_name: Optional[str] = None
    indicator_unit: Optional[str] = None
    location_id: int
    location_name: Optional[str] = None
    value: float
    period: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "indicator_id": 2,
                "indicator_name": "consecutive_rainy_days",
                "indicator_short_name": "crd",
                "indicator_unit": "days",
                "location_id": 10,
                "location_name": "Palmira",
                "value": 5.0,
                "period": "monthly",
                "start_date": "2024-01-01T00:00:00Z",
                "end_date": "2024-01-31T00:00:00Z"
            }
        }

router = APIRouter(tags=["Climate Historical Indicator"], prefix="/indicator")

@router.get("/by-indicator-name", response_model=List[ClimateHistoricalIndicatorRecord])
def get_by_indicator_name(
    indicator_name: str = Query(..., description="Indicator name")
):
    """
    Returns historical indicator records filtered by indicator name.
    - **indicator_name**: Name of the indicator to filter records by.
    """
    service = ClimateHistoricalIndicatorService()
    data = service.get_by_indicator_name(indicator_name)
    return [
        ClimateHistoricalIndicatorRecord(
            id=d.id,
            indicator_id=d.indicator_id,
            indicator_name=getattr(d.indicator, "name", None),
            indicator_short_name=getattr(d.indicator, "short_name", None),
            indicator_unit=getattr(d.indicator, "unit", None),
            location_id=d.location_id,
            location_name=getattr(d.location, "name", None),
            value=d.value,
            period=d.period,
            start_date=d.start_date,
            end_date=d.end_date
        ) for d in data
    ]

@router.get("/by-location-id", response_model=List[ClimateHistoricalIndicatorRecord])
def get_by_location_id(
    location_id: int = Query(..., description="Location ID")
):
    """
    Returns historical indicator records filtered by location ID.
    - **location_id**: ID of the location to filter records by.
    """
    service = ClimateHistoricalIndicatorService()
    data = service.get_by_location_id(location_id)
    return [
        ClimateHistoricalIndicatorRecord(
            id=d.id,
            indicator_id=d.indicator_id,
            indicator_name=getattr(d.indicator, "name", None),
            indicator_short_name=getattr(d.indicator, "short_name", None),
            indicator_unit=getattr(d.indicator, "unit", None),
            location_id=d.location_id,
            location_name=getattr(d.location, "name", None),
            value=d.value,
            period=d.period,
            start_date=d.start_date,
            end_date=d.end_date
        ) for d in data
    ]

@router.get("/by-location-and-indicator-name", response_model=List[ClimateHistoricalIndicatorRecord])
def get_by_location_and_indicator_name(
    location_name: str = Query(..., description="Location name"),
    indicator_name: str = Query(..., description="Indicator name")
):
    """
    Returns historical indicator records filtered by location name and indicator name.
    - **location_name**: Name of the location to filter records by.
    - **indicator_name**: Name of the indicator to filter records by.
    """
    service = ClimateHistoricalIndicatorService()
    data = service.get_by_location_and_indicator_name(location_name, indicator_name)
    return [
        ClimateHistoricalIndicatorRecord(
            id=d.id,
            indicator_id=d.indicator_id,
            indicator_name=getattr(d.indicator, "name", None),
            indicator_short_name=getattr(d.indicator, "short_name", None),
            indicator_unit=getattr(d.indicator, "unit", None),
            location_id=d.location_id,
            location_name=getattr(d.location, "name", None),
            value=d.value,
            period=d.period,
            start_date=d.start_date,
            end_date=d.end_date
        ) for d in data
    ]

@router.get("/by-period", response_model=List[ClimateHistoricalIndicatorRecord])
def get_by_period(
    period: str = Query(..., description="Period type (e.g. monthly, yearly)")
):
    """
    Returns historical indicator records filtered by period type.
    - **period**: Type of period to filter records by (e.g., 'monthly', 'yearly').
    """
    service = ClimateHistoricalIndicatorService()
    period_upper = period.upper()
    try:
        data = service.get_by_period(period_upper)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid period: {period}")
    return [
        ClimateHistoricalIndicatorRecord(
            id=d.id,
            indicator_id=d.indicator_id,
            indicator_name=getattr(d.indicator, "name", None),
            indicator_short_name=getattr(d.indicator, "short_name", None),
            indicator_unit=getattr(d.indicator, "unit", None),
            location_id=d.location_id,
            location_name=getattr(d.location, "name", None),
            value=d.value,
            period=d.period,
            start_date=d.start_date,
            end_date=d.end_date
        ) for d in data
    ]

@router.get("/by-date-range", response_model=List[ClimateHistoricalIndicatorRecord])
def get_by_date_range(
    start_date: str = Query(..., description="Start date (YYYY-MM-DD)"),
    end_date: str = Query(..., description="End date (YYYY-MM-DD)")
):
    """
    Returns historical indicator records for all indicators and locations within a date range.
    - **start_date**: Start date for the range of historical indicator data (format: YYYY-MM-DD).
    - **end_date**: End date for the range of historical indicator data (format: YYYY-MM-DD).
    """
    service = ClimateHistoricalIndicatorService()
    data = service.get_by_date_range(start_date, end_date)
    return [
        ClimateHistoricalIndicatorRecord(
            id=d.id,
            indicator_id=d.indicator_id,
            indicator_name=getattr(d.indicator, "name", None),
            indicator_short_name=getattr(d.indicator, "short_name", None),
            indicator_unit=getattr(d.indicator, "unit", None),
            location_id=d.location_id,
            location_name=getattr(d.location, "name", None),
            value=d.value,
            period=d.period,
            start_date=d.start_date,
            end_date=d.end_date
        ) for d in data
    ]

@router.get("/by-indicator-and-location", response_model=List[ClimateHistoricalIndicatorRecord])
def get_by_indicator_and_location(
    indicator_id: int = Query(..., description="Indicator ID"),
    location_id: int = Query(..., description="Location ID")
):
    """
    Returns historical indicator records filtered by indicator ID and location ID.
    - **indicator_id**: ID of the indicator to filter records by.
    - **location_id**: ID of the location to filter records by.
    """
    service = ClimateHistoricalIndicatorService()
    data = service.get_by_indicator_and_location(indicator_id, location_id)
    return [
        ClimateHistoricalIndicatorRecord(
            id=d.id,
            indicator_id=d.indicator_id,
            indicator_name=getattr(d.indicator, "name", None),
            indicator_short_name=getattr(d.indicator, "short_name", None),
            indicator_unit=getattr(d.indicator, "unit", None),
            location_id=d.location_id,
            location_name=getattr(d.location, "name", None),
            value=d.value,
            period=d.period,
            start_date=d.start_date,
            end_date=d.end_date
        ) for d in data
    ]

@router.get("/by-location-date-period", response_model=List[ClimateHistoricalIndicatorRecord])
def get_by_location_date_period(
    location_id: int = Query(..., description="Location ID"),
    start_date: str = Query(..., description="Start date (YYYY-MM-DD)"),
    end_date: str = Query(..., description="End date (YYYY-MM-DD)"),
    period: str = Query(..., description="Period type (e.g. monthly, yearly)")
):
    """
    Returns historical indicator records filtered by:
    - Location ID
    - Date range (inclusive)
    - Period type
    
    Example: /by-location-date-period?location_id=123&start_date=2023-01-01&end_date=2023-12-31&period=monthly
    """
    service = ClimateHistoricalIndicatorService()
    
    # Validación adicional para fechas
    if start_date > end_date:
        raise HTTPException(
            status_code=400, 
            detail="Start date cannot be after end date"
        )
    
    period_upper = period.upper()
    data = service.get_by_location_date_period(location_id, start_date, end_date, period_upper)
    
    return [
        ClimateHistoricalIndicatorRecord(
            id=d.id,
            indicator_id=d.indicator_id,
            indicator_name=d.indicator.name if d.indicator else None,
            indicator_short_name=d.indicator.short_name if d.indicator else None,
            indicator_unit=d.indicator.unit if d.indicator else None,
            location_id=d.location_id,
            location_name=d.location.name if d.location else None,
            value=d.value,
            period=d.period,
            start_date=d.start_date,
            end_date=d.end_date
        ) for d in data
    ]
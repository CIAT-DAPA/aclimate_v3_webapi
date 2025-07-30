from fastapi import APIRouter, Query, HTTPException
from typing import List
from aclimate_v3_orm.services.climate_historical_indicator_service import ClimateHistoricalIndicatorService

router = APIRouter(tags=["Climate Historical Indicator"], prefix="/indicator")

@router.get("/by-indicator-name", response_model=List[dict])
def get_by_indicator_name(
    indicator_name: str = Query(..., description="Indicator name")
):
    """
    Returns historical indicator records filtered by indicator name.
    - **indicator_name**: Name of the indicator to filter records by.
    """
    service = ClimateHistoricalIndicatorService()
    data = service.get_by_indicator_name(indicator_name)
    result = [
        {
            "id": d.id,
            "indicator_id": d.indicator_id,
            "indicator_name": getattr(d.indicator, "name", None),
            "indicator_short_name": getattr(d.indicator, "short_name", None),
            "indicator_unit": getattr(d.indicator, "unit", None),
            "location_id": d.location_id,
            "location_name": getattr(d.location, "name", None),
            "value": d.value,
            "period": d.period,
            "start_date": d.start_date,
            "end_date": d.end_date
        }
        for d in data
    ]
    return result

@router.get("/by-location-id", response_model=List[dict])
def get_by_location_id(
    location_id: int = Query(..., description="Location ID")
):
    """
    Returns historical indicator records filtered by location ID.
    - **location_id**: ID of the location to filter records by.
    """
    service = ClimateHistoricalIndicatorService()
    data = service.get_by_location_id(location_id)
    result = [
        {
            "id": d.id,
            "indicator_id": d.indicator_id,
            "indicator_name": getattr(d.indicator, "name", None),
            "indicator_short_name": getattr(d.indicator, "short_name", None),
            "indicator_unit": getattr(d.indicator, "unit", None),
            "location_id": d.location_id,
            "location_name": getattr(d.location, "name", None),
            "value": d.value,
            "period": d.period,
            "start_date": d.start_date,
            "end_date": d.end_date
        }
        for d in data
    ]
    return result

@router.get("/by-location-and-indicator-name", response_model=List[dict])
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
    result = [
        {
            "id": d.id,
            "indicator_id": d.indicator_id,
            "indicator_name": getattr(d.indicator, "name", None),
            "indicator_short_name": getattr(d.indicator, "short_name", None),
            "indicator_unit": getattr(d.indicator, "unit", None),
            "location_id": d.location_id,
            "location_name": getattr(d.location, "name", None),
            "value": d.value,
            "period": d.period,
            "start_date": d.start_date,
            "end_date": d.end_date
        }
        for d in data
    ]
    return result

@router.get("/by-period", response_model=List[dict])
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
    result = [
        {
            "id": d.id,
            "indicator_id": d.indicator_id,
            "indicator_name": getattr(d.indicator, "name", None),
            "indicator_short_name": getattr(d.indicator, "short_name", None),
            "indicator_unit": getattr(d.indicator, "unit", None),
            "location_id": d.location_id,
            "location_name": getattr(d.location, "name", None),
            "value": d.value,
            "period": d.period,
            "start_date": d.start_date,
            "end_date": d.end_date
        }
        for d in data
    ]
    return result

@router.get("/by-date-range", response_model=List[dict])
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
    result = [
        {
            "id": d.id,
            "indicator_id": d.indicator_id,
            "indicator_name": getattr(d.indicator, "name", None),
            "indicator_short_name": getattr(d.indicator, "short_name", None),
            "indicator_unit": getattr(d.indicator, "unit", None),
            "location_id": d.location_id,
            "location_name": getattr(d.location, "name", None),
            "value": d.value,
            "period": d.period,
            "start_date": d.start_date,
            "end_date": d.end_date
        }
        for d in data
    ]
    return result

@router.get("/by-indicator-and-location", response_model=List[dict])
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
    result = [
        {
            "id": d.id,
            "indicator_id": d.indicator_id,
            "indicator_name": getattr(d.indicator, "name", None),
            "indicator_short_name": getattr(d.indicator, "short_name", None),
            "indicator_unit": getattr(d.indicator, "unit", None),
            "location_id": d.location_id,
            "location_name": getattr(d.location, "name", None),
            "value": d.value,
            "period": d.period,
            "start_date": d.start_date,
            "end_date": d.end_date
        }
        for d in data
    ]
    return result

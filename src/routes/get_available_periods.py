from fastapi import APIRouter
from typing import List
from pydantic import BaseModel
from sqlalchemy import exists
from sqlalchemy.orm import Session
from aclimate_v3_orm.database import SessionLocal
from aclimate_v3_orm.models.climate_historical_indicator import ClimateHistoricalIndicator

class PeriodResponse(BaseModel):
    value: str
    label: str
    has_data: bool

    class Config:
        json_schema_extra = {
            "example": {
                "value": "annual",
                "label": "Annual",
                "has_data": True
            }
        }

router = APIRouter(tags=["Periods"], prefix="/periods")

def check_indicator_period_has_data(session: Session, period: str, location_id: int) -> bool:
    """Check if indicators table has at least one record for a specific period and location"""
    try:
        return session.query(
            exists().where(
                (ClimateHistoricalIndicator.period == period) & 
                (ClimateHistoricalIndicator.location_id == location_id)
            )
        ).scalar()
    except:
        return False

@router.get("/available", response_model=List[PeriodResponse])
def get_available_periods(location_id: int):
    """
    Returns a list of periods (daily, monthly, annual, seasonal, decadal, other) 
    indicating which ones have data available for a specific location in the climate_historical_indicator table.
    
    This endpoint checks the climate_historical_indicator table for different period types
    filtered by location.
    
    Parameters:
    - **location_id**: ID of the location/station to check for available periods
    
    Returns:
    - **value**: Period identifier (lowercase)
    - **label**: Human-readable period name
    - **has_data**: Boolean indicating if there's data for this period
    """
    
    db = SessionLocal()
    
    try:
        # Check for indicator periods for the specific location
        has_daily = check_indicator_period_has_data(db, "DAILY", location_id)
        has_monthly = check_indicator_period_has_data(db, "MONTHLY", location_id)
        has_annual = check_indicator_period_has_data(db, "ANNUAL", location_id)
        has_seasonal = check_indicator_period_has_data(db, "SEASONAL", location_id)
        has_decadal = check_indicator_period_has_data(db, "DECADAL", location_id)
        has_other = check_indicator_period_has_data(db, "OTHER", location_id)
        
        # Prepare response
        periods = [
            PeriodResponse(
                value="daily", 
                label="Daily", 
                has_data=has_daily
            ),
            PeriodResponse(
                value="monthly", 
                label="Monthly", 
                has_data=has_monthly
            ),
            PeriodResponse(
                value="annual", 
                label="Annual", 
                has_data=has_annual
            ),
            PeriodResponse(
                value="seasonal", 
                label="Seasonal", 
                has_data=has_seasonal
            ),
            PeriodResponse(
                value="decadal", 
                label="Decadal", 
                has_data=has_decadal
            ),
            PeriodResponse(
                value="other", 
                label="Other", 
                has_data=has_other
            ),
        ]
        
        return periods
    finally:
        db.close()

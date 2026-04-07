from typing import Optional
from pydantic import BaseModel
from datetime import date, datetime


class ClimateHistoricalClimatology(BaseModel):
    id: int
    location_id: int
    location_name: Optional[str]
    measure_id: Optional[int]
    measure_name: Optional[str]
    measure_short_name: Optional[str]
    measure_unit: Optional[str]
    month: int
    value: float

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "location_id": 114,
                "location_name": "SOPROCOM LA CONCORDIA",
                "measure_id": 4,
                "measure_name": "Humedad relativa calculada máxima diaria",
                "measure_short_name": "hrmax",
                "measure_unit": "% (porcentaje)",
                "month": 1,
                "value": 90.16
            }
        }


class ClimateHistoricalDaily(BaseModel):
    id: int
    location_id: int
    location_name: Optional[str]
    measure_id: Optional[int]
    measure_name: Optional[str]
    measure_short_name: Optional[str]
    measure_unit: Optional[str]
    date: date
    value: float

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "location_id": 103,
                "location_name": "LACHORRERA",
                "measure_id": 7,
                "measure_name": "Minimum temperature",
                "measure_short_name": "tmin",
                "measure_unit": "°C",
                "date": "1996-11-01",
                "value": 23.0
            }
        }


class ClimateHistoricalMonthly(BaseModel):
    id: int
    location_id: int
    location_name: Optional[str]
    measure_id: Optional[int]
    measure_name: Optional[str]
    measure_short_name: Optional[str]
    measure_unit: Optional[str]
    date: date
    value: float

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "location_id": 7,
                "location_name": "VILLAGARZON",
                "measure_id": 7,
                "measure_name": "Minimum temperature",
                "measure_short_name": "tmin",
                "measure_unit": "°C",
                "date": "1996-10-01",
                "value": 20.71
            }
        }


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


class MinMaxClimatologyRecord(BaseModel):
    measure_id: int
    measure_name: Optional[str] = None
    location_id: int
    location_name: Optional[str] = None
    min_value: float
    min_month: Optional[int] = None
    max_value: float
    max_month: Optional[int] = None

    class Config:
        json_schema_extra = {
            "example": {
                "measure_id": 2,
                "measure_name": "precipitation",
                "location_id": 10,
                "location_name": "Palmira",
                "min_value": 0.0,
                "min_month": "1",
                "max_value": 100.0,
                "max_month": "2"
            }
        }


class MinMaxDailyRecord(BaseModel):
    measure_id: int
    measure_name: Optional[str] = None
    location_id: int
    location_name: Optional[str] = None
    min_value: float
    min_date: Optional[datetime] = None
    max_value: float
    max_date: Optional[datetime] = None

    class Config:
        json_schema_extra = {
            "example": {
                "measure_id": 2,
                "measure_name": "precipitation",
                "location_id": 10,
                "location_name": "Palmira",
                "min_value": 0.0,
                "min_date": "2024-01-01T00:00:00Z",
                "max_value": 100.0,
                "max_date": "2024-01-31T00:00:00Z"
            }
        }


class MinMaxMonthlyRecord(BaseModel):
    measure_id: int
    measure_name: Optional[str] = None
    location_id: int
    location_name: Optional[str] = None
    min_value: float
    min_date: Optional[datetime] = None
    max_value: float
    max_date: Optional[datetime] = None

    class Config:
        json_schema_extra = {
            "example": {
                "measure_id": 2,
                "measure_name": "precipitation",
                "location_id": 10,
                "location_name": "Palmira",
                "min_value": 0.0,
                "min_date": "2024-01-01T00:00:00Z",
                "max_value": 100.0,
                "max_date": "2024-01-31T00:00:00Z"
            }
        }


class MinMaxIndicatorRecord(BaseModel):
    indicator_id: int
    indicator_name: Optional[str] = None
    location_id: int
    location_name: Optional[str] = None
    min_value: float
    min_date: Optional[datetime] = None
    max_value: float
    max_date: Optional[datetime] = None

    class Config:
        json_schema_extra = {
            "example": {
                "indicator_id": 2,
                "indicator_name": "consecutive_rainy_days",
                "location_id": 10,
                "location_name": "Palmira",
                "min_value": 1.0,
                "min_date": "2024-01-01T00:00:00Z",
                "max_value": 10.0,
                "max_date": "2024-01-31T00:00:00Z"
            }
        }

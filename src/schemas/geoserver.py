from typing import List, Literal, Optional, Dict
from pydantic import BaseModel, field_validator
from datetime import date


class Coordinate(BaseModel):
    lon: float
    lat: float

    class Config:
        json_schema_extra = {
            "example": {
                "lon": -74.0817,
                "lat": 4.6097
            }
        }


class PointDataRequest(BaseModel):
    coordinates: List[List[float]]
    start_date: date
    end_date: Optional[date] = None
    workspace: str
    store: str
    temporality: Literal["daily", "monthly", "annual"] = "daily"

    @field_validator('end_date')
    @classmethod
    def validate_date_range(cls, v, info):
        start = info.data.get('start_date')
        if v is None:
            return start
        if v < start:
            raise ValueError('end_date must be >= start_date')
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "coordinates": [[-74.0817, 4.6097], [-75.5, 6.2]],
                "start_date": "2024-01-01",
                "end_date": "2024-01-31",
                "workspace": "aclimate",
                "store": "precipitation",
                "temporality": "daily"
            }
        }


class PointDataResult(BaseModel):
    coordinate: List[float]
    date: str
    value: float

    class Config:
        json_schema_extra = {
            "example": {
                "coordinate": [-74.0817, 4.6097],
                "date": "2024-01-15",
                "value": 12.5
            }
        }


class PointDataResponse(BaseModel):
    total_results: int
    data: List[PointDataResult]

    class Config:
        json_schema_extra = {
            "example": {
                "total_results": 2,
                "data": [
                    {
                        "coordinate": [-74.0817, 4.6097],
                        "date": "2024-01-15",
                        "value": 12.5
                    }
                ]
            }
        }


class ClipGeoserverSource(BaseModel):
    workspace: str
    layer: str
    cql_filter: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "workspace": "aclimate",
                "layer": "country_boundaries",
                "cql_filter": "name = 'Colombia'"
            }
        }


class ClipConfig(BaseModel):
    enabled: bool = False
    geoserver: Optional[ClipGeoserverSource] = None

    class Config:
        json_schema_extra = {
            "example": {
                "enabled": True,
                "geoserver": {
                    "workspace": "aclimate",
                    "layer": "country_boundaries",
                    "cql_filter": "name = 'Colombia'"
                }
            }
        }


class RasterExportRequest(BaseModel):
    workspace: str
    store: str
    start_date: date
    end_date: Optional[date] = None
    temporality: Literal["daily", "monthly", "annual"] = "daily"
    clip: ClipConfig = ClipConfig()
    output_format: Literal["single_tiff", "zip"] = "zip"

    @field_validator('end_date')
    @classmethod
    def validate_date_range(cls, v, info):
        start = info.data.get('start_date')
        if v is None:
            return start
        if v < start:
            raise ValueError('end_date must be >= start_date')
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "workspace": "aclimate",
                "store": "precipitation",
                "start_date": "2024-01-01",
                "end_date": "2024-01-07",
                "temporality": "daily",
                "clip": {
                    "enabled": False,
                    "geoserver": None
                },
                "output_format": "zip"
            }
        }

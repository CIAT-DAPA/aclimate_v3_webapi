from typing import List, Literal
from pydantic import BaseModel
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
    end_date: date
    workspace: str
    store: str
    temporality: Literal["daily", "monthly", "annual"] = "daily"

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

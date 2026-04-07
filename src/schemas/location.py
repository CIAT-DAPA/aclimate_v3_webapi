from typing import Optional, List
from pydantic import BaseModel


class Country(BaseModel):
    id: int
    name: str
    iso2: str

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "name": "COLOMBIA",
                "iso2": "CO"
            }
        }


class Admin1(BaseModel):
    id: int
    name: str
    ext_id: str
    country_id: int
    country_name: str
    country_iso2: str

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "name": "Putumayo",
                "ext_id": "86",
                "country_id": 3,
                "country_name": "AMAZONIA",
                "country_iso2": "ST"
            }
        }


class Admin2(BaseModel):
    id: int
    name: str
    ext_id: str
    admin1_id: int | None
    admin1_name: str | None
    admin1_ext_id: str | None
    country_id: int | None
    country_name: str | None
    country_iso2: str | None

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "name": "Mocoa",
                "ext_id": "86001",
                "admin1_id": 1,
                "admin1_name": "Putumayo",
                "admin1_ext_id": "86",
                "country_id": 3,
                "country_name": "AMAZONIA",
                "country_iso2": "ST"
            }
        }


class Location(BaseModel):
    id: int
    name: str
    ext_id: Optional[str] = None
    machine_name: Optional[str] = None
    enable: Optional[bool] = None
    altitude: Optional[float] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    visible: Optional[bool] = True
    admin2_id: Optional[int] = None
    admin2_name: Optional[str] = None
    admin2_ext_id: Optional[str] = None
    admin1_id: Optional[int] = None
    admin1_name: Optional[str] = None
    admin1_ext_id: Optional[str] = None
    country_id: Optional[int] = None
    country_name: Optional[str] = None
    country_iso2: Optional[str] = None
    source: Optional[str] = None

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "name": "CAMPUCANA",
                "ext_id": "44010030",
                "machine_name": "campucana",
                "enable": True,
                "altitude": 1400.0,
                "latitude": 1.2025,
                "longitude": -76.68083333,
                "visible": True,
                "admin2_id": 1,
                "admin2_name": "Mocoa",
                "admin2_ext_id": "86001",
                "admin1_id": 1,
                "admin1_name": "Putumayo",
                "admin1_ext_id": "86",
                "country_id": 3,
                "country_name": "AMAZONIA",
                "country_iso2": "ST",
                "source": "IDEAM"
            }
        }


class MeasureData(BaseModel):
    """Climate measure data"""
    measure_id: int
    measure_name: str
    measure_short_name: str
    measure_unit: Optional[str]
    value: Optional[float]

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "measure_id": 7,
                "measure_name": "Minimum temperature",
                "measure_short_name": "tmin",
                "measure_unit": "°C",
                "value": 20.71
            }
        }


class LatestData(BaseModel):
    """Latest monitoring data for a location"""
    date: Optional[str]
    measures: List[MeasureData] = []

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "date": "1996-10-01",
                "measures": [
                    {
                        "measure_id": 7,
                        "measure_name": "Minimum temperature",
                        "measure_short_name": "tmin",
                        "measure_unit": "°C",
                        "value": 20.71
                    }
                ]
            }
        }


class LocationWithData(BaseModel):
    """Location with its latest monitoring data"""
    id: int
    name: str
    ext_id: Optional[str]
    machine_name: Optional[str]
    enable: Optional[bool]
    altitude: Optional[float]
    latitude: Optional[float]
    longitude: Optional[float]
    visible: Optional[bool] = True
    source_id: Optional[int]
    source_name: Optional[str]
    source_type: Optional[str]
    admin2_id: Optional[int]
    admin2_name: Optional[str]
    admin2_ext_id: Optional[str]
    admin1_id: Optional[int]
    admin1_name: Optional[str]
    admin1_ext_id: Optional[str]
    country_id: int
    country_name: Optional[str]
    country_iso2: Optional[str]
    latest_data: Optional[LatestData]

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "name": "CAMPUCANA",
                "ext_id": "44010030",
                "machine_name": "campucana",
                "enable": True,
                "altitude": 1400.0,
                "latitude": 1.2025,
                "longitude": -76.68083333,
                "visible": True,
                "source_id": 1,
                "source_name": "IDEAM",
                "source_type": "observational",
                "admin2_id": 1,
                "admin2_name": "Mocoa",
                "admin2_ext_id": "86001",
                "admin1_id": 1,
                "admin1_name": "Putumayo",
                "admin1_ext_id": "86",
                "country_id": 3,
                "country_name": "AMAZONIA",
                "country_iso2": "ST",
                "latest_data": {
                    "date": "1996-10-01",
                    "measures": [
                        {
                            "measure_id": 7,
                            "measure_name": "Minimum temperature",
                            "measure_short_name": "tmin",
                            "measure_unit": "°C",
                            "value": 20.71
                        }
                    ]
                }
            }
        }

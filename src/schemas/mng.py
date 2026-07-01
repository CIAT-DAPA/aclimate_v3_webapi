from typing import Optional, List, Dict
from pydantic import BaseModel


class CountryIndicator(BaseModel):
    id: int
    country_id: int
    indicator_id: int
    spatial_forecast: bool
    spatial_climate: bool
    location_forecast: bool
    location_climate: bool
    criteria: Optional[Dict] = None
    description: Optional[str] = None
    store: Optional[str] = None
    workspace: Optional[str] = None

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "country_id": 1,
                "indicator_id": 2,
                "spatial_forecast": True,
                "spatial_climate": False,
                "location_forecast": True,
                "location_climate": True,
                "criteria": {"admin_level": 2, "threshold": 0.5},
                "description": "Descripción del indicador para este país",
                "store": "precipitation_data",
                "workspace": "default_workspace"
            }
        }


class ClimateMeasure(BaseModel):
    id: int
    name: str
    short_name: str
    unit: str
    description: Optional[str] = None
    enable: bool

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "name": "Precipitación",
                "short_name": "prec",
                "unit": "mm",
                "description": "Precipitación total acumulada",
                "enable": True
            }
        }


class IndicatorCategory(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    enable: bool

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "name": "Temperaturas Extremas",
                "description": "Estos indicadores describen las variaciones y extremos en las condiciones de temperatura.",
                "enable": True
            }
        }


class IndicatorFeature(BaseModel):
    id: int
    country_indicator_id: Optional[int] = None
    title: str
    description: Optional[str] = None
    type: str

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "country_indicator_id": 1,
                "title": "Temperature Management",
                "description": "Best practices for managing temperature stress",
                "type": "recommendation"
            }
        }


class Indicator(BaseModel):
    id: int
    name: str
    short_name: str
    unit: str
    type: str
    temporality: str
    indicator_category_id: int
    description: Optional[str] = None
    enable: bool

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 7,
                "name": "Días fríos",
                "short_name": "TX10p",
                "unit": "% días/año",
                "type": "CLIMATE",
                "temporality": "ANNUAL",
                "indicator_category_id": 1,
                "description": "Cantidad total de días con temperaturas por debajo del percentil 10.",
                "enable": True
            }
        }


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


class IndicatorWithFeatures(Indicator):
    features: Optional[List[IndicatorFeature]] = []

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 7,
                "name": "Días fríos",
                "short_name": "TX10p",
                "unit": "% días/año",
                "type": "CLIMATE",
                "temporality": "ANNUAL",
                "indicator_category_id": 1,
                "description": "Cantidad total de días con temperaturas por debajo del percentil 10.",
                "enable": True,
                "features": []
            }
        }

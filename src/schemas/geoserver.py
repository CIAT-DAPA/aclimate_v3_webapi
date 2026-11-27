import re
from typing import Any, List, Literal, Optional, Dict, Union
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator
from datetime import date


class Coordinate(BaseModel):
    lon: float
    lat: float

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "lon": -74.0817,
                "lat": 4.6097
            }
        },
    )


# Month in MM format ("01" to "12"), used by the "climatology" temporality
MONTH_PATTERN = re.compile(r"^(0[1-9]|1[0-2])$")


def validate_range_for_temporality(request):
    """
    Check that start_date and end_date of a request use the format required by its temporality.

    - "climatology": months in MM format ("01" to "12").
    - "daily", "monthly" and "annual": dates in YYYY-MM-DD format.

    - request: Model with start_date, end_date and temporality attributes.

    Returns the same request, with end_date defaulted to start_date when it was not sent.
    Raises ValueError when a value does not match the temporality or the range is inverted.
    """
    # When end_date is not sent the range is a single date (or month)
    if request.end_date is None:
        request.end_date = request.start_date
    if request.temporality == "climatology":
        # Climatology works with months: both values must be in MM format
        for field_name in ("start_date", "end_date"):
            value = getattr(request, field_name)
            # Full dates and invalid months (e.g. "13", "1") are rejected
            if not isinstance(value, str) or not MONTH_PATTERN.match(value):
                raise ValueError(
                    f"{field_name} must be a month in MM format (01-12) when temporality is 'climatology'"
                )
        # The range must not end before it starts (both are zero-padded, so text order is month order)
        if request.end_date < request.start_date:
            raise ValueError('end_date must be >= start_date')
    else:
        # Daily, monthly and annual work with full dates
        for field_name in ("start_date", "end_date"):
            # Anything that is not a valid date (e.g. a month like "01") is rejected
            if not isinstance(getattr(request, field_name), date):
                raise ValueError(
                    f"{field_name} must be a date in YYYY-MM-DD format when temporality is '{request.temporality}'"
                )
    return request


class PointDataRequest(BaseModel):
    """
    Request body for /geoserver/point-data.

    start_date and end_date depend on the temporality:
    - "daily", "monthly" and "annual": dates in YYYY-MM-DD format.
    - "climatology": months in MM format ("01" to "12"), because a climatology
      has one raster per month and no year.
    """
    coordinates: List[List[float]]
    # left_to_right: a value is read as a date when possible and kept as text (a month) otherwise
    start_date: Union[date, str] = Field(union_mode='left_to_right')
    end_date: Optional[Union[date, str]] = Field(default=None, union_mode='left_to_right')
    workspace: str
    store: str
    temporality: Literal["daily", "monthly", "annual", "climatology"] = "daily"

    @field_validator('end_date')
    @classmethod
    def validate_date_range(cls, v, info):
        """Default end_date to start_date and reject date ranges that end before they start."""
        start = info.data.get('start_date')
        # When end_date is not sent the range is a single date (or month)
        if v is None:
            return start
        # Only two full dates are compared here; months are validated in validate_temporality_format
        if isinstance(v, date) and isinstance(start, date) and v < start:
            raise ValueError('end_date must be >= start_date')
        return v

    @model_validator(mode='after')
    def validate_temporality_format(self):
        """Check that start_date and end_date use the format required by the temporality."""
        return validate_range_for_temporality(self)

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "coordinates": [[-74.0817, 4.6097], [-75.5, 6.2]],
                "start_date": "2024-01-01",
                "end_date": "2024-01-31",
                "workspace": "aclimate",
                "store": "precipitation",
                "temporality": "daily"
            }
        },
    )


class PointDataResult(BaseModel):
    coordinate: List[float]
    date: str
    value: float

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "coordinate": [-74.0817, 4.6097],
                "date": "2024-01-15",
                "value": 12.5
            }
        },
    )


class PointDataResponse(BaseModel):
    total_results: int
    data: List[PointDataResult]

    model_config = ConfigDict(
        json_schema_extra={
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
        },
    )


class PolygonDataRequest(BaseModel):
    """
    Request body for /geoserver/polygon-data.

    - polygon: GeoJSON (EPSG:4326) used to clip the rasters. It can be a Polygon or
      MultiPolygon geometry, a Feature or a FeatureCollection.
    - start_date: Start date of the range (YYYY-MM-DD). For "climatology", start month in MM format.
    - end_date: End date of the range (defaults to start_date). For "climatology", end month in MM format.
    - workspace: Geoserver workspace.
    - store: Geoserver store/mosaic.
    - temporality: Time frequency ("daily", "monthly", "annual" or "climatology").
    """
    polygon: Dict[str, Any]
    # left_to_right: a value is read as a date when possible and kept as text (a month) otherwise
    start_date: Union[date, str] = Field(union_mode='left_to_right')
    end_date: Optional[Union[date, str]] = Field(default=None, union_mode='left_to_right')
    workspace: str
    store: str
    temporality: Literal["daily", "monthly", "annual", "climatology"] = "daily"

    @field_validator('end_date')
    @classmethod
    def validate_date_range(cls, v, info):
        """Default end_date to start_date and reject date ranges that end before they start."""
        start = info.data.get('start_date')
        # When end_date is not sent the range is a single date (or month)
        if v is None:
            return start
        # Only two full dates are compared here; months are validated in validate_temporality_format
        if isinstance(v, date) and isinstance(start, date) and v < start:
            raise ValueError('end_date must be >= start_date')
        return v

    @model_validator(mode='after')
    def validate_temporality_format(self):
        """Check that start_date and end_date use the format required by the temporality."""
        return validate_range_for_temporality(self)

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "polygon": {
                    "type": "Polygon",
                    "coordinates": [[
                        [-86.6, 12.9], [-86.1, 12.9], [-86.1, 13.4], [-86.6, 13.4], [-86.6, 12.9]
                    ]]
                },
                "start_date": "2024-01-01",
                "end_date": "2024-01-03",
                "workspace": "climate_historical_daily",
                "store": "climate_historical_daily_ni_prec",
                "temporality": "daily"
            }
        },
    )


class AdminAreaLayer(BaseModel):
    """
    Layer with administrative areas available in GeoServer.

    - layer: Layer name, used to request its polygons.
    - prefix: Text before "_adm{n}" in the layer name (country name, ISO2 or region).
      None when the layer name does not follow that convention.
    - level: Administrative level (0 = country, 1 = admin 1, 2 = admin 2, ...).
      None when the layer name does not follow that convention.
    """
    layer: str
    prefix: Optional[str] = None
    level: Optional[int] = None

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "layer": "colombia_adm1",
                "prefix": "colombia",
                "level": 1
            }
        },
    )


class ClipGeoserverSource(BaseModel):
    workspace: str
    layer: str
    cql_filter: Optional[str] = None

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "workspace": "aclimate",
                "layer": "country_boundaries",
                "cql_filter": "name = 'Colombia'"
            }
        },
    )


class ClipConfig(BaseModel):
    enabled: bool = False
    geoserver: Optional[ClipGeoserverSource] = None

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "enabled": True,
                "geoserver": {
                    "workspace": "aclimate",
                    "layer": "country_boundaries",
                    "cql_filter": "name = 'Colombia'"
                }
            }
        },
    )


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

    model_config = ConfigDict(
        json_schema_extra={
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
        },
    )

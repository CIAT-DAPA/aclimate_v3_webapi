from schemas.location import Country, Admin1, Admin2, Location, MeasureData, LatestData, LocationWithData
from schemas.climate import (
    ClimateHistoricalMonthRecord,
    ClimateHistoricalDateRecord,
    ClimateHistoricalIndicatorRecord,
    MinMaxMonthRecord,
    MinMaxDateRecord,
)
from schemas.mng import CountryIndicator, IndicatorCategory, IndicatorFeature, Indicator, IndicatorWithFeatures
from schemas.geoserver import (
    Coordinate, PointDataRequest, PointDataResult, PointDataResponse,
    ClipGeoserverSource, ClipConfig, RasterExportRequest,
)
from schemas.auth import (
    Credential,
    UserCreateRequest,
    CreateRoleRequest,
    DeleteUserRequest,
    SafeUserUpdate,
    RoleAssignmentByIdRequest,
    RoleRemovalByIdRequest,
)

__all__ = [
    # location
    "Country", "Admin1", "Admin2", "Location",
    "MeasureData", "LatestData", "LocationWithData",
    # climate
    "ClimateHistoricalMonthRecord", "ClimateHistoricalDateRecord",
    "ClimateHistoricalIndicatorRecord",
    "MinMaxMonthRecord", "MinMaxDateRecord",
    # mng
    "CountryIndicator", "IndicatorCategory", "IndicatorFeature",
    "Indicator", "IndicatorWithFeatures",
    # geoserver
    "Coordinate", "PointDataRequest", "PointDataResult",
    "PointDataResponse", "ClipGeoserverSource", "ClipConfig",
    "RasterExportRequest",
    # auth
    "Credential", "UserCreateRequest", "CreateRoleRequest",
    "DeleteUserRequest", "SafeUserUpdate",
    "RoleAssignmentByIdRequest", "RoleRemovalByIdRequest",
]

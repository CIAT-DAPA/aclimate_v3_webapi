from schemas.location import Country, Admin1, Admin2, Location, MeasureData, LatestData, LocationWithData
from schemas.climate import (
    ClimateHistoricalClimatology,
    ClimateHistoricalDaily,
    ClimateHistoricalMonthly,
    ClimateHistoricalIndicatorRecord,
    MinMaxClimatologyRecord,
    MinMaxDailyRecord,
    MinMaxMonthlyRecord,
    MinMaxIndicatorRecord,
)
from schemas.mng import CountryIndicator, IndicatorCategory, IndicatorFeature, Indicator, IndicatorWithFeatures
from schemas.geoserver import Coordinate, PointDataRequest, PointDataResult
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
    "ClimateHistoricalClimatology", "ClimateHistoricalDaily",
    "ClimateHistoricalMonthly", "ClimateHistoricalIndicatorRecord",
    "MinMaxClimatologyRecord", "MinMaxDailyRecord",
    "MinMaxMonthlyRecord", "MinMaxIndicatorRecord",
    # mng
    "CountryIndicator", "IndicatorCategory", "IndicatorFeature",
    "Indicator", "IndicatorWithFeatures",
    # geoserver
    "Coordinate", "PointDataRequest", "PointDataResult",
    # auth
    "Credential", "UserCreateRequest", "CreateRoleRequest",
    "DeleteUserRequest", "SafeUserUpdate",
    "RoleAssignmentByIdRequest", "RoleRemovalByIdRequest",
]

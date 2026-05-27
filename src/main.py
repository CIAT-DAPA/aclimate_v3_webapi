from fastapi import FastAPI, Depends
from aclimate_v3_orm.migrations import upgrade, current, downgrade
from dependencies.auth_dependencies import get_current_user
from auth.auth import router as auth_router
from auth.token_validation_router import router as validate_token_router
from routes.root_redirect import router as root_redirect_router
from routes.get_all_countries import router as get_all_countries_router
from routes.get_countries_by_name import router as get_countries_by_name_router
from routes.get_admin1_by_country_id import router as get_admin1_by_country_id_router
from routes.get_adm1_by_adm1_name import router as get_admin1_by_adm1_name_router
from routes.get_adm2_by_country_id import router as get_adm2_by_country_id_router
from routes.get_adm2_by_name import router as get_adm2_by_name_router
from routes.get_climate_historical_monthly_by_all_measures import router as get_climate_historical_monthly_by_adm1_name_router
from routes.get_climate_historical_climatology_by_all_measures import router as get_climate_historical_climatology_by_location_name_router
from routes.get_climate_historical_indicator import router as get_climate_historical_indicator_router
from routes.get_mng_indicators import router as get_mng_indicators_router
from routes.get_mng_indicator_categories import router as get_mng_indicator_categories_router
from routes.get_mng_indicator_features import router as get_mng_indicator_features_router
from routes.minmax_indicator_by_location import router as minmax_indicator_by_location_router
from routes.minmax_daily_by_location import router as minmax_daily_by_location_router
from routes.minmax_monthly_by_location import router as minmax_monthly_by_location_router
from routes.minmax_climatology_by_location import router as minmax_climatology_by_location_router
from routes.get_climate_historical_daily_by_date_ranges_and_all_measures import router as get_climate_historical_daily_by_date_ranges_and_all_measures_router
from routes.get_locations_by_name import router as get_locations_by_name_router
from routes.get_locations_by_id import router as get_locations_by_id_router
from routes.get_locations_with_data import router as get_locations_with_latest_data_router
from auth.get_client_token import router as get_client_token_router
# Geoserver route
from routes.get_geoserver_point_data import router as get_geoserver_point_data_router
# Periods route
from routes.get_available_periods import router as get_available_periods_router
from fastapi.middleware.cors import CORSMiddleware
from aclimate_v3_orm.database.base import create_tables

app = FastAPI(
    title="Aclimate v3 API",
    version="3.0",
    description="API for Aclimate including various administrative levels and climate data."
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

_auth = [Depends(get_current_user)]

# Routers
app.include_router(root_redirect_router)
app.include_router(auth_router)
app.include_router(validate_token_router)

app.include_router(get_all_countries_router, dependencies=_auth)
app.include_router(get_countries_by_name_router, dependencies=_auth)
app.include_router(get_admin1_by_country_id_router, dependencies=_auth)
app.include_router(get_admin1_by_adm1_name_router, dependencies=_auth)

app.include_router(get_adm2_by_country_id_router, dependencies=_auth)
app.include_router(get_adm2_by_name_router, dependencies=_auth)
app.include_router(get_locations_by_name_router, dependencies=_auth)
app.include_router(get_locations_by_id_router, dependencies=_auth)
app.include_router(get_locations_with_latest_data_router, dependencies=_auth)

app.include_router(get_climate_historical_monthly_by_adm1_name_router, dependencies=_auth)
app.include_router(get_climate_historical_climatology_by_location_name_router, dependencies=_auth)

app.include_router(get_climate_historical_indicator_router, dependencies=_auth)
app.include_router(get_mng_indicators_router, dependencies=_auth)
app.include_router(get_mng_indicator_categories_router, dependencies=_auth)
app.include_router(get_mng_indicator_features_router, dependencies=_auth)

app.include_router(minmax_indicator_by_location_router, dependencies=_auth)
app.include_router(minmax_daily_by_location_router, dependencies=_auth)
app.include_router(minmax_monthly_by_location_router, dependencies=_auth)
app.include_router(minmax_climatology_by_location_router, dependencies=_auth)

app.include_router(get_client_token_router)
app.include_router(get_climate_historical_daily_by_date_ranges_and_all_measures_router, dependencies=_auth)

# Geoserver router
app.include_router(get_geoserver_point_data_router, dependencies=_auth)

# Periods router
app.include_router(get_available_periods_router, dependencies=_auth)


def startup_event():
    print(" Creando tablas al iniciar...")
    create_tables()

def Apply_migrations():
    print(" Applying migrations...")
    upgrade()
    print(" Migrations applied.")
    
#startup_event
#Apply_migrations()
#uvicorn main:app --reload

# 🌦️ AClimate V3 API

## 🏷️ Version & Tags

![GitHub release (latest by date)](https://img.shields.io/github/v/release/CIAT-DAPA/aclimate_v3_webapi) ![](https://img.shields.io/github/v/tag/CIAT-DAPA/aclimate_v3_webapi)

---

## 📌 Introduction

AClimate V3 API provides RESTful endpoints to access climate data, forecasts, and administrative information for the AClimate platform. Built with **FastAPI**, it integrates authentication and authorization with **Keycloak** for secure access.

This API exposes data models (countries, locations, admin levels, climate data) through a consistent and clean interface.

---

## Features

- 🚀 **FastAPI**-based high-performance REST API  
- 🔐 **Keycloak** integration for authentication and role-based authorization  
- 🌐 Simplified data access: climate historical, monthly, climatology, locations, admin levels  
- 🧩 Modular router structure  
- 📚 Auto-generated Swagger & ReDoc documentation  

---

## ✅ Requirements

- Python >= 3.10  
- [uv](https://docs.astral.sh/uv/) to manage the environment and dependencies  
- **Keycloak** running and configured for user management and token issuance  
- Relational database (PostgreSQL)  
- Dependencies: FastAPI, Pydantic, SQLAlchemy, psycopg2, python-dotenv, uvicorn, python-keycloak, jose  

---

## 🔐 Authentication & Authorization

The API uses **Keycloak** for OAuth2 password grant authentication.  
To access secured endpoints:

1️⃣ Start Keycloak and configure a realm, client, and users.  
2️⃣ Obtain a JWT token from Keycloak.  
3️⃣ Include the token in the Authorization header of your API requests.


## 🔐 Authentication Example

Include your Keycloak token in the Authorization header:

Authorization: Bearer <access_token>

---

## 🚀 Installation Steps

Clone the repository and install dependencies:

```bash
git clone https://github.com/CIAT-DAPA/aclimate_v3_api.git
cd aclimate_v3_webapi
uv sync
```

`uv sync` creates the `.venv` environment with Python 3.10 and installs the exact versions pinned in `uv.lock`
(use `uv sync --no-dev` to skip the test dependencies).

To add or update a dependency use `uv add <package>` / `uv lock --upgrade-package <package>` and commit
both `pyproject.toml` and `uv.lock`.
## 🌱 Set the Environment Variables

Set up the environment variables in a `.env` file:
```bash
DATABASE_URL=postgresql://username:password@localhost:5432/database
KEYCLOAK_URL=http://localhost:8080
REALM_NAME=<realm>
CLIENT_ID=<client-id>
CLIENT_SECRET=<client-secret>
GEOSERVER_URL=<geoserver-url>
GEOSERVER_USER=<geoserver-user>
GEOSERVER_PASSWORD=<geoserver-password>
MAX_WORKERS=4
MAX_SYNC_DAYS=7
HEALTH_TOKEN=<health-token>
```

The file must be placed in `src/.env` (see `src/.env.example`). The `GEOSERVER_*` variables are
required by the `/geoserver/*` endpoints and `MAX_WORKERS` sets how many rasters are downloaded in
parallel.
## 🚀 Run the API

```bash
cd src
uv run uvicorn main:app --reload
```

## 🧪 Run the tests

```bash
uv run pytest
```

---

## 📚 Endpoints

The full interactive documentation is available in `/docs` (Swagger) and `/redoc` once the API is
running. All the endpoints below require the `Authorization: Bearer <access_token>` header.

### `GET /countries`

Returns every enabled country with its `id`, `name`, `iso2` and two configuration lists:

- **conf_climate**: climate measures configured for the country. Each item merges the country
  configuration (`mng_country_climate_measure`) with the measure data (`mng_climate_measure`).
- **conf_indicator**: indicators configured for the country. Each item merges the country
  configuration (`mng_country_indicator`) with the indicator (`mng_indicators`) and its category
  (`mng_indicator_category`).

Each item is a single flat object and no IDs are exposed inside both lists. Only enabled measures
and indicators are included; a country without configuration returns empty lists.

```json
[
  {
    "id": 4,
    "name": "NICARAGUA",
    "iso2": "NI",
    "conf_climate": [
      {
        "name": "Precipitación",
        "short_name": "prec",
        "unit": "mm",
        "description": "Precipitación total acumulada",
        "country_description": null,
        "spatial_forecast": false,
        "spatial_climate": true,
        "location_forecast": false,
        "location_climate": true,
        "spatial_climate_conf": [
          {
            "temporality": "daily",
            "store": "climate_historical_daily_ni_prec",
            "workspace": "climate_historical_daily"
          }
        ],
        "location_climate_conf": ["daily", "monthly", "climatology"]
      }
    ],
    "conf_indicator": [
      {
        "type": "climate",
        "name": "Días fríos",
        "short_name": "TX10p",
        "unit": "% días/año",
        "temporality": "annual",
        "description": "Cantidad total de días con temperaturas por debajo del percentil 10.",
        "category_name": "Temperaturas Extremas",
        "category_description": "Variaciones y extremos en las condiciones de temperatura.",
        "country_description": null,
        "spatial_forecast": false,
        "spatial_climate": true,
        "location_forecast": false,
        "location_climate": true,
        "criteria": { "admin_level": 2, "threshold": 0.5 },
        "store": "climate_index_annual_ni_tx10p",
        "workspace": "climate_index"
      }
    ]
  }
]
```

> `GET /countries/by-name` returns the same entity, but `conf_climate` and `conf_indicator` are
> always empty.

### `POST /geoserver/polygon-data`

Gets the rasters of a date range clipped by a polygon. It works like `/geoserver/point-data`, but
instead of a JSON with point values it returns the clipped rasters.

| Parameter | Description |
|---|---|
| `polygon` | GeoJSON (EPSG:4326) with the polygon to cut data: `Polygon`, `MultiPolygon`, `Feature` or `FeatureCollection` |
| `start_date` | Start date of the range (`YYYY-MM-DD`) |
| `end_date` | End date of the range (optional, defaults to `start_date`) |
| `workspace` | Geoserver workspace |
| `store` | Geoserver store/mosaic |
| `temporality` | Time frequency: `daily` (default), `monthly` or `annual` |

Request example:

```json
{
  "polygon": {
    "type": "Polygon",
    "coordinates": [[[-86.6, 12.9], [-86.1, 12.9], [-86.1, 13.4], [-86.6, 13.4], [-86.6, 12.9]]]
  },
  "start_date": "2024-01-01",
  "end_date": "2024-01-03",
  "workspace": "climate_historical_daily",
  "store": "climate_historical_daily_ni_prec",
  "temporality": "daily"
}
```

Response: a ZIP file (`application/zip`) with one GeoTIFF per date, named `{date}.tif`
(e.g. `2024-01-01.tif`; monthly and annual rasters use the first day of the month/year).

- Every pixel touched by the polygon is included, so a polygon smaller than a pixel still returns
  data. Pixels inside the clipped extent but outside the polygon are set to nodata.
- Dates without raster in GeoServer are skipped.
- There is no limit on the number of dates; all the clipped rasters are kept in memory to build
  the ZIP, so very long ranges are slower and use more memory.

| Status | When |
|---|---|
| `200` | ZIP file with the clipped rasters |
| `400` | The polygon is not a valid GeoJSON polygon |
| `404` | No date has data, or the polygon is outside the raster |
| `422` | Missing fields or `end_date` before `start_date` |
| `500` | GeoServer credentials not configured or unexpected error |

```bash
curl -X POST "http://localhost:8000/geoserver/polygon-data" \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d @request.json \
  -o polygon_rasters.zip
```

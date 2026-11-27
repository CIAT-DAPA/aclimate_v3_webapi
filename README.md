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
GEOSERVER_ADMIN_WORKSPACE=administrative
GEOSERVER_ADMIN_MAX_FEATURES=100
MAX_WORKERS=4
MAX_SYNC_DAYS=7
HEALTH_TOKEN=<health-token>
```

The file must be placed in `src/.env` (see `src/.env.example`). The `GEOSERVER_*` variables are
required by the `/geoserver/*` endpoints and `MAX_WORKERS` sets how many rasters are downloaded in
parallel. `GEOSERVER_ADMIN_WORKSPACE` is the workspace with the administrative areas (default
`administrative`) and `GEOSERVER_ADMIN_MAX_FEATURES` the maximum number of polygons returned by one
search (default `100`).
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

### `POST /geoserver/point-data`

Gets the values of a raster for a list of coordinates within a range.

| Parameter | Description |
|---|---|
| `coordinates` | List of coordinates `[[lon, lat], [lon, lat]]` |
| `start_date` | Start of the range: `YYYY-MM-DD`, or month in `MM` format for `climatology` |
| `end_date` | End of the range (optional, defaults to `start_date`): `YYYY-MM-DD`, or month in `MM` format for `climatology` |
| `workspace` | Geoserver workspace |
| `store` | Geoserver store/mosaic |
| `temporality` | Time frequency: `daily` (default), `monthly`, `annual` or `climatology` |

A climatology has one raster per month and no year, so with `"temporality": "climatology"` the
range is given in months (`"01"` to `"12"`) and each result is identified by its month:

```json
{
  "coordinates": [[-86.25, 12.13]],
  "start_date": "01",
  "end_date": "03",
  "workspace": "climate_historical_climatology",
  "store": "climate_historical_climatology_ni_prec",
  "temporality": "climatology"
}
```

```json
{
  "total_results": 3,
  "data": [
    { "coordinate": [-86.25, 12.13], "date": "01", "value": 12.5 },
    { "coordinate": [-86.25, 12.13], "date": "02", "value": 30.1 },
    { "coordinate": [-86.25, 12.13], "date": "03", "value": 48.7 }
  ]
}
```

Sending a full date with `climatology`, or a month with any other temporality, answers `422`.

> The climatology rasters are requested to GeoServer with the reference year `2000`
> (`2000-01-01`, `2000-02-01`, ...). The place to change when the mosaics are published only by
> month is marked with `###AJUSTAR FORMATO CLIMATOLOGY###` in `src/services/geoserver.py`.

### `POST /geoserver/polygon-data`

Gets the rasters of a date range clipped by a polygon. It works like `/geoserver/point-data`, but
instead of a JSON with point values it returns the clipped rasters.

| Parameter | Description |
|---|---|
| `polygon` | GeoJSON (EPSG:4326) with the polygon to cut data: `Polygon`, `MultiPolygon`, `Feature` or `FeatureCollection` |
| `start_date` | Start of the range: `YYYY-MM-DD`, or month in `MM` format for `climatology` |
| `end_date` | End of the range (optional, defaults to `start_date`): `YYYY-MM-DD`, or month in `MM` format for `climatology` |
| `workspace` | Geoserver workspace |
| `store` | Geoserver store/mosaic |
| `temporality` | Time frequency: `daily` (default), `monthly`, `annual` or `climatology` |

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
With `climatology` the range is given in months (`"start_date": "01", "end_date": "03"`), as in
`/geoserver/point-data`, and the files are named by month (`01.tif`, `02.tif`, `03.tif`). Ranges
that cross the year (e.g. `11` to `02`) are rejected with `422`.

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

### `GET /geoserver/admin-areas/layers`

Returns the layers with administrative areas published in the GeoServer workspace configured in
`GEOSERVER_ADMIN_WORKSPACE`. The list is cached in memory for 5 minutes.

```json
[
  { "layer": "colombia_adm0", "prefix": "colombia", "level": 0 },
  { "layer": "colombia_adm1", "prefix": "colombia", "level": 1 },
  { "layer": "et_adm3_wp", "prefix": "et", "level": 3 },
  { "layer": "sat_amazonia_area_drenajes", "prefix": null, "level": null }
]
```

- `level` is the administrative level: `0` = country, `1` = admin 1, `2` = admin 2, etc.
- `prefix` is the text before `_adm{level}` in the layer name (country name, ISO2 or region).
- Both are `null` when the layer name does not follow the `{prefix}_adm{level}` convention.

### `GET /geoserver/admin-areas/polygon`

Returns the polygons of an administrative area as GeoJSON.

| Parameter | Description |
|---|---|
| `layer` | Layer name, as returned by `/geoserver/admin-areas/layers` (e.g. `colombia_adm1`) |
| `description` | Text to search in the attributes of the layer (e.g. `Valle del Cauca`) |

Each layer has its own attribute names, so the description is searched in **every text attribute**
of the layer, with a partial and case-insensitive match (`valle` finds `Valle del Cauca`). All the
polygons that match are returned (up to `GEOSERVER_ADMIN_MAX_FEATURES`).

```bash
curl -G "http://localhost:8000/geoserver/admin-areas/polygon" \
  -H "Authorization: Bearer <access_token>" \
  --data-urlencode "layer=colombia_adm1" \
  --data-urlencode "description=Valle del Cauca"
```

Response: a GeoJSON `FeatureCollection` in EPSG:4326 with the original attributes of the layer in
`properties` (the attribute names depend on the layer):

```json
{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "id": "colombia_adm1.31",
      "geometry": { "type": "MultiPolygon", "coordinates": [[[[-76.5, 3.1], [-76.4, 3.1], [-76.4, 3.2], [-76.5, 3.1]]]] },
      "properties": { "ADM1_ES": "Valle del Cauca", "ADM1_PCODE": "CO76" }
    }
  ]
}
```

The response can be sent as the `polygon` of `POST /geoserver/polygon-data` to get the rasters
clipped by that administrative area.

| Status | When |
|---|---|
| `200` | GeoJSON with the polygons that match |
| `404` | The layer does not exist in the workspace, or no polygon matches the description |
| `422` | `layer` or `description` missing or empty |
| `500` | GeoServer credentials not configured or unexpected error |
| `502` | GeoServer is not available or returned an error |

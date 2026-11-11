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
KEYCLOAK_REALM=<realm>
KEYCLOAK_CLIENT_ID=<client-id>
KEYCLOAK_CLIENT_SECRET=<client-secret>
```
## 🚀 Run the API

```bash
cd src
uv run uvicorn main:app --reload
```

## 🧪 Run the tests

```bash
uv run pytest
```

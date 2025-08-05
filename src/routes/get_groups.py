from fastapi import APIRouter, Depends, HTTPException
import requests
import os
from dependencies.auth_dependencies import require_roles

router = APIRouter(
    prefix="/groups",
    tags=["Webadmin"]
)


@router.get("/list", summary="List all groups from Keycloak")
def list_keycloak_groups(
    current_user: dict = Depends(require_roles(["adminsuper"]))
):
    # Environment variables
    KEYCLOAK_URL = os.getenv("KEYCLOAK_URL", "http://localhost:8080")
    REALM_NAME = os.getenv("REALM_NAME", "aclimate")
    CLIENT_ID_NAME = os.getenv("CLIENT_ID", "dummy-client")
    CLIENT_SECRET = os.getenv("CLIENT_SECRET")

    # Step 1: Get admin token using client credentials
    token_resp = requests.post(
        f"{KEYCLOAK_URL}/realms/{REALM_NAME}/protocol/openid-connect/token",
        data={
            "grant_type": "client_credentials",
            "client_id": CLIENT_ID_NAME,
            "client_secret": CLIENT_SECRET
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    if token_resp.status_code != 200:
        raise HTTPException(status_code=401, detail="Failed to obtain admin token")
    token = token_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Step 2: Get all groups
    groups_resp = requests.get(
        f"{KEYCLOAK_URL}/admin/realms/{REALM_NAME}/groups",
        headers=headers
    )
    if groups_resp.status_code != 200:
        raise HTTPException(status_code=groups_resp.status_code, detail="Failed to fetch groups")
    groups = groups_resp.json()
    # Return only id and name for each group
    return [{"id": g["id"], "name": g["name"]} for g in groups]
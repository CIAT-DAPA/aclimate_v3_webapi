from fastapi import APIRouter, Depends, HTTPException, Body
import requests
import os
from dependencies.auth_dependencies import require_roles

router = APIRouter(
    prefix="/groups",
    tags=["Webadmin"]
)

@router.post("/create", summary="Create a new group in Keycloak")
def create_keycloak_group(
    group_name: str = Body(..., embed=True),
    current_user: dict = Depends(require_roles(["adminsuper"]))
):
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
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    # Step 2: Create group
    group_data = {"name": group_name}
    create_resp = requests.post(
        f"{KEYCLOAK_URL}/admin/realms/{REALM_NAME}/groups",
        headers=headers,
        json=group_data
    )
    if create_resp.status_code not in (201, 204):
        raise HTTPException(status_code=create_resp.status_code, detail=f"Failed to create group: {create_resp.text}")
    return {"message": "Group created successfully", "name": group_name}

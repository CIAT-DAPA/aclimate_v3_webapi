from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
import os
import httpx
from dependencies.auth_dependencies import require_roles

router = APIRouter(
    prefix="/roles",
    tags=["Webadmin"]
)

class CreateRoleRequest(BaseModel):
    name: str
    description: str | None = None
    composite: bool = False

async def get_admin_token():
    KEYCLOAK_URL = os.getenv("KEYCLOAK_URL")
    REALM_NAME = os.getenv("REALM_NAME")
    CLIENT_ID = os.getenv("CLIENT_ID")
    CLIENT_SECRET = os.getenv("CLIENT_SECRET")

    data = {
        "grant_type": "client_credentials",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    url = f"{KEYCLOAK_URL}/realms/{REALM_NAME}/protocol/openid-connect/token"

    async with httpx.AsyncClient() as client:
        response = await client.post(url, data=data, headers=headers)

    if response.status_code != 200:
        raise HTTPException(status_code=401, detail="Failed to obtain admin token")
    
    return response.json()["access_token"]

@router.post("/create", summary="Create a new client role in Keycloak")
async def create_client_role(
    request: CreateRoleRequest,
    current_user: dict = Depends(require_roles(["adminsuper"]))
):
    KEYCLOAK_URL = os.getenv("KEYCLOAK_URL")
    REALM_NAME = os.getenv("REALM_NAME")
    CLIENT_ID = os.getenv("CLIENT_ID")
    token = await get_admin_token()

    async with httpx.AsyncClient() as client:
        # Step 1: Get client internal ID
        client_resp = await client.get(
            f"{KEYCLOAK_URL}/admin/realms/{REALM_NAME}/clients?clientId={CLIENT_ID}",
            headers={"Authorization": f"Bearer {token}"}
        )
        if client_resp.status_code != 200 or not client_resp.json():
            raise HTTPException(status_code=404, detail=f"Client '{CLIENT_ID}' not found")
        client_id = client_resp.json()[0]["id"]

        # Step 2: Create the role
        role_data = {
            "name": request.name,
            "description": request.description,
            "composite": request.composite,
            "clientRole": True
        }

        create_resp = await client.post(
            f"{KEYCLOAK_URL}/admin/realms/{REALM_NAME}/clients/{client_id}/roles",
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            },
            json=role_data
        )

        if create_resp.status_code not in (201, 204):
            raise HTTPException(status_code=500, detail="Failed to create role")

    return {
        "message": f"Role '{request.name}' successfully created in client '{CLIENT_ID}'"
    }

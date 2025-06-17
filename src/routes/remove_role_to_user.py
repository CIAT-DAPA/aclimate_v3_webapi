from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
import os
import httpx
from dependencies.auth_dependencies import require_roles

router = APIRouter(
    prefix="/users",
    tags=["Webadmin"]
)

class RoleRemovalByIdRequest(BaseModel):
    user_id: str
    role_id: str


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


@router.post("/remove-role", summary="Remove a client role from a user using role ID")
async def remove_role_by_id(
    request: RoleRemovalByIdRequest,
    current_user: dict = Depends(require_roles(["adminsuper"]))
):
    KEYCLOAK_URL = os.getenv("KEYCLOAK_URL")
    REALM_NAME = os.getenv("REALM_NAME")
    CLIENT_ID = os.getenv("CLIENT_ID")
    token = await get_admin_token()

    async with httpx.AsyncClient() as client:
        # Step 1: Get internal client ID
        client_resp = await client.get(
            f"{KEYCLOAK_URL}/admin/realms/{REALM_NAME}/clients?clientId={CLIENT_ID}",
            headers={"Authorization": f"Bearer {token}"}
        )
        if client_resp.status_code != 200 or not client_resp.json():
            raise HTTPException(status_code=404, detail=f"Client '{CLIENT_ID}' not found")
        client_id = client_resp.json()[0]["id"]

        # Step 2: Get all roles to match role ID
        roles_resp = await client.get(
            f"{KEYCLOAK_URL}/admin/realms/{REALM_NAME}/clients/{client_id}/roles",
            headers={"Authorization": f"Bearer {token}"}
        )
        if roles_resp.status_code != 200:
            raise HTTPException(status_code=500, detail="Failed to retrieve client roles")

        all_roles = roles_resp.json()
        role = next((r for r in all_roles if r["id"] == request.role_id), None)
        if not role:
            raise HTTPException(status_code=404, detail=f"Role ID '{request.role_id}' not found in client '{CLIENT_ID}'")

        # Step 3: Remove role from user
        remove_resp = await client.request(
            method="DELETE",
            url=f"{KEYCLOAK_URL}/admin/realms/{REALM_NAME}/users/{request.user_id}/role-mappings/clients/{client_id}",
            headers={"Authorization": f"Bearer {token}"},
            json=[{
                "id": role["id"],
                "name": role["name"]
            }]
        )
        if remove_resp.status_code != 204:
            raise HTTPException(status_code=500, detail="Failed to remove role from user")

    return {
        "message": f"Role '{role['name']}' successfully removed from user with ID '{request.user_id}'"
    }

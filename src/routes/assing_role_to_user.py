from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
import os
import httpx
from dependencies.auth_dependencies import require_roles

router = APIRouter(
    prefix="/users",
    tags=["Webadmin"]
)

# Environment variables



async def get_admin_token():
    KEYCLOAK_URL = os.getenv("KEYCLOAK_URL")
    REALM_NAME = os.getenv("REALM_NAME")
    CLIENT_ID = os.getenv("CLIENT_ID")
    CLIENT_SECRET = os.getenv("CLIENT_SECRET")
    """Obtain an access token using client credentials."""
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


class RoleAssignmentByIdRequest(BaseModel):
    user_id: str
    role_id: str


@router.post("/assign-role", summary="Assign a client role to a user using IDs")
async def assign_role_by_id(
    request: RoleAssignmentByIdRequest,
    current_user: dict = Depends(require_roles(["adminsuper"]))
):
    KEYCLOAK_URL = os.getenv("KEYCLOAK_URL")
    REALM_NAME = os.getenv("REALM_NAME")
    CLIENT_ID = os.getenv("CLIENT_ID")
    CLIENT_SECRET = os.getenv("CLIENT_SECRET")
    token = await get_admin_token()

    async with httpx.AsyncClient() as client:
        # Step 1: Get client ID from env
        client_resp = await client.get(
            f"{KEYCLOAK_URL}/admin/realms/{REALM_NAME}/clients?clientId={CLIENT_ID}",
            headers={"Authorization": f"Bearer {token}"}
        )
        if client_resp.status_code != 200 or not client_resp.json():
            raise HTTPException(status_code=404, detail=f"Client '{CLIENT_ID}' not found")
        client_id = client_resp.json()[0]["id"]

        # Step 2: Get role details by ID (you must fetch it from the role list)
        roles_resp = await client.get(
            f"{KEYCLOAK_URL}/admin/realms/{REALM_NAME}/clients/{client_id}/roles",
            headers={"Authorization": f"Bearer {token}"}
        )
        if roles_resp.status_code != 200:
            raise HTTPException(status_code=500, detail="Failed to retrieve roles for client")

        all_roles = roles_resp.json()
        role = next((r for r in all_roles if r["id"] == request.role_id), None)
        if not role:
            raise HTTPException(status_code=404, detail=f"Role ID '{request.role_id}' not found in client '{CLIENT_ID}'")

        # Step 3: Assign the role to the user by ID
        assign_resp = await client.post(
            f"{KEYCLOAK_URL}/admin/realms/{REALM_NAME}/users/{request.user_id}/role-mappings/clients/{client_id}",
            headers={"Authorization": f"Bearer {token}"},
            json=[{
                "id": role["id"],
                "name": role["name"]
            }]
        )
        if assign_resp.status_code not in (204, 201):
            raise HTTPException(status_code=500, detail="Failed to assign role to user")

    return {
        "message": f"Role '{role['name']}' successfully assigned to user with ID '{request.user_id}'"
    }

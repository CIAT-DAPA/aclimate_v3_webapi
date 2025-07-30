from fastapi import APIRouter, Depends, HTTPException
import os
import httpx
from dependencies.auth_dependencies import require_roles  # Your existing validator

router = APIRouter(
    prefix="/users",
    tags=["Webadmin"]
)




async def get_admin_token():
    # Environment variables
    KEYCLOAK_URL = os.getenv("KEYCLOAK_URL")
    REALM_NAME = os.getenv("REALM_NAME")
    CLIENT_ID = os.getenv("CLIENT_ID")
    CLIENT_SECRET = os.getenv("CLIENT_SECRET")
    """Get a token using client credentials grant."""
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
        print("Keycloak error:", response.text)
        raise HTTPException(status_code=401, detail="Invalid client credentials")
    return response.json()["access_token"]


@router.get("/get-client-roles", summary="Get all roles for the configured client")
async def get_client_roles(current_user: dict = Depends(require_roles(["adminsuper"]))):
    KEYCLOAK_URL = os.getenv("KEYCLOAK_URL")
    REALM_NAME = os.getenv("REALM_NAME")
    CLIENT_ID = os.getenv("CLIENT_ID")
    CLIENT_SECRET = os.getenv("CLIENT_SECRET")
    token = await get_admin_token()

    async with httpx.AsyncClient() as client:
        # Step 1: Get the client UUID from its clientId (e.g., 'aclimate_client')
        client_resp = await client.get(
            f"{KEYCLOAK_URL}/admin/realms/{REALM_NAME}/clients?clientId={CLIENT_ID}",
            headers={"Authorization": f"Bearer {token}"}
        )
        if client_resp.status_code != 200 or not client_resp.json():
            raise HTTPException(status_code=500, detail="Failed to retrieve client ID")
        
        client_id = client_resp.json()[0]["id"]

        # Step 2: Fetch all roles for that client
        roles_resp = await client.get(
            f"{KEYCLOAK_URL}/admin/realms/{REALM_NAME}/clients/{client_id}/roles",
            headers={"Authorization": f"Bearer {token}"}
        )
        if roles_resp.status_code != 200:
            raise HTTPException(status_code=500, detail="Failed to retrieve client roles")

        roles = roles_resp.json()
    
    return {
        "client_id": client_id,
        "role_count": len(roles),
        "roles": roles
    }

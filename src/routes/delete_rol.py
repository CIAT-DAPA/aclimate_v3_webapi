from fastapi import APIRouter, Depends, HTTPException
import os
import httpx
from dependencies.auth_dependencies import require_roles

router = APIRouter(
    prefix="/roles",
    tags=["Webadmin"]
)

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

@router.delete("/delete/{role_id}", summary="Delete any role in Keycloak by ID")
async def delete_role_by_id(
    role_id: str,
    current_user: dict = Depends(require_roles(["adminsuper"]))
):
    KEYCLOAK_URL = os.getenv("KEYCLOAK_URL")
    REALM_NAME = os.getenv("REALM_NAME")
    token = await get_admin_token()

    async with httpx.AsyncClient() as client:
        delete_url = f"{KEYCLOAK_URL}/admin/realms/{REALM_NAME}/roles-by-id/{role_id}"
        delete_resp = await client.delete(
            delete_url,
            headers={"Authorization": f"Bearer {token}"}
        )

        if delete_resp.status_code != 204:
            raise HTTPException(
                status_code=404 if delete_resp.status_code == 404 else 500,
                detail="Failed to delete role (does it exist and do you have permissions?)"
            )

    return {
        "message": f"Role with id '{role_id}' successfully deleted from realm '{REALM_NAME}'"
    }

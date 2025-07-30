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
KEYCLOAK_URL = os.getenv("KEYCLOAK_URL")
REALM_NAME = os.getenv("REALM_NAME")
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")


async def get_admin_token():
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


class DeleteUserRequest(BaseModel):
    user_id: str


@router.delete("/delete-user", summary="Delete a user from Keycloak by ID")
async def delete_user(
    request: DeleteUserRequest,
    current_user: dict = Depends(require_roles(["adminsuper"]))
):
    token = await get_admin_token()

    async with httpx.AsyncClient() as client:
        delete_resp = await client.delete(
            f"{KEYCLOAK_URL}/admin/realms/{REALM_NAME}/users/{request.user_id}",
            headers={"Authorization": f"Bearer {token}"}
        )

        if delete_resp.status_code == 204:
            return {"message": f"User with ID '{request.user_id}' was successfully deleted"}
        elif delete_resp.status_code == 404:
            raise HTTPException(status_code=404, detail="User not found")
        else:
            raise HTTPException(
                status_code=delete_resp.status_code,
                detail=f"Failed to delete user: {delete_resp.text}"
            )

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict
import os
import httpx
from dependencies.auth_dependencies import require_roles  # Your existing validator

router = APIRouter(
    prefix="/users",
    tags=["Webadmin"]
)

# Environment variables
KEYCLOAK_URL = os.getenv("KEYCLOAK_URL")
REALM_NAME = os.getenv("REALM_NAME")
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")


class Credential(BaseModel):
    type: str = "password"
    value: str
    temporary: bool = False


class UserCreateRequest(BaseModel):
    username: str
    email: str
    firstName: Optional[str] = ""
    lastName: Optional[str] = ""
    emailVerified: Optional[bool] = False
    enabled: Optional[bool] = True
    attributes: Optional[Dict[str, str]] = None
    credentials: List[Credential]


async def get_admin_token():
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


@router.post("/create-user", summary="Create a Keycloak user and assign webadminsimple role")
async def create_user(
    request: UserCreateRequest,
    current_user: dict = Depends(require_roles(["adminsuper"]))
):
    token = await get_admin_token()

    user_payload = {
        "username": request.username,
        "email": request.email,
        "enabled": request.enabled,
        "emailVerified": request.emailVerified,
        "firstName": request.firstName or "",
        "lastName": request.lastName or "",
        "credentials": [cred.dict() for cred in request.credentials],
        "attributes": request.attributes or {}
    }


    async with httpx.AsyncClient() as client:
        # Step 1: Create the user
        create_resp = await client.post(
            f"{KEYCLOAK_URL}/admin/realms/{REALM_NAME}/users",
            headers={"Authorization": f"Bearer {token}"},
            json=user_payload,
        )
        if create_resp.status_code not in (201, 204):
            print("User creation error:", create_resp.text)
            raise HTTPException(status_code=500, detail="Failed to create user")

        # Step 2: Retrieve the user ID
        users_resp = await client.get(
            f"{KEYCLOAK_URL}/admin/realms/{REALM_NAME}/users?username={request.username}",
            headers={"Authorization": f"Bearer {token}"}
        )
        if users_resp.status_code != 200 or not users_resp.json():
            raise HTTPException(status_code=500, detail="Failed to retrieve user ID")
        user_id = users_resp.json()[0]["id"]

        # Step 3: Get client ID by clientId name
        client_resp = await client.get(
            f"{KEYCLOAK_URL}/admin/realms/{REALM_NAME}/clients?clientId={CLIENT_ID}",
            headers={"Authorization": f"Bearer {token}"}
        )
        if client_resp.status_code != 200 or not client_resp.json():
            raise HTTPException(status_code=500, detail="Failed to retrieve client ID")
        client_id = client_resp.json()[0]["id"]

        # Step 4: Get the webadminsimple role from the client
        role_resp = await client.get(
            f"{KEYCLOAK_URL}/admin/realms/{REALM_NAME}/clients/{client_id}/roles/webadminsimple",
            headers={"Authorization": f"Bearer {token}"}
        )
        if role_resp.status_code != 200:
            raise HTTPException(status_code=500, detail="Failed to retrieve 'webadminsimple' role")
        role_data = role_resp.json()
        
        # Step 5: Assign the role to the user
        assign_resp = await client.post(
            f"{KEYCLOAK_URL}/admin/realms/{REALM_NAME}/users/{user_id}/role-mappings/clients/{client_id}",
            headers={"Authorization": f"Bearer {token}"},
            json=[{
                "id": role_data["id"],
                "name": role_data["name"]
            }]
        )
        if assign_resp.status_code not in (204, 201):
            print("Role assignment error:", assign_resp.text)
            raise HTTPException(status_code=500, detail="Failed to assign 'webadminsimple' role")

    return {
        "message": "User created and 'webadminsimple' role assigned successfully",
        "user_id": user_id
    }

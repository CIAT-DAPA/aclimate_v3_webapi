from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List
import os
import httpx
from dependencies.auth_dependencies import require_roles

router = APIRouter(
    prefix="/users",
    tags=["Webadmin"]
)

KEYCLOAK_URL = os.getenv("KEYCLOAK_URL")
REALM_NAME = os.getenv("REALM_NAME")

class AssignGroupsRequest(BaseModel):
    user_id: str
    groups: List[str]

async def get_admin_token():
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

@router.post("/assign-groups", summary="Assign one or more groups to a Keycloak user")
async def assign_groups_by_id(
    request: AssignGroupsRequest,
    current_user: dict = Depends(require_roles(["adminsuper"]))
):
    token = await get_admin_token()
    async with httpx.AsyncClient() as client:
        # Get all groups from Keycloak
        groups_resp = await client.get(
            f"{KEYCLOAK_URL}/admin/realms/{REALM_NAME}/groups",
            headers={"Authorization": f"Bearer {token}"}
        )
        if groups_resp.status_code != 200 or not groups_resp.json():
            raise HTTPException(status_code=404, detail="No groups found in Keycloak")
        all_groups = groups_resp.json()
        group_id_map = {g["name"]: g["id"] for g in all_groups}
        assigned = []
        for group_name in request.groups:
            group_id = group_id_map.get(group_name)
            if not group_id:
                raise HTTPException(status_code=404, detail=f"Group '{group_name}' not found in Keycloak")
            assign_resp = await client.put(
                f"{KEYCLOAK_URL}/admin/realms/{REALM_NAME}/users/{request.user_id}/groups/{group_id}",
                headers={"Authorization": f"Bearer {token}"}
            )
            if assign_resp.status_code not in (204, 201):
                raise HTTPException(status_code=500, detail=f"Failed to assign user to group '{group_name}'")
            assigned.append(group_name)
    return {
        "message": f"Groups {assigned} successfully assigned to user with ID '{request.user_id}'",
        "user_id": request.user_id,
        "groups_assigned": assigned
    }

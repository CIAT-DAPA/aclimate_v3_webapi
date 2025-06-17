from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr
import requests
import os
from dependencies.auth_dependencies import require_roles

router = APIRouter(
    prefix="/users",
    tags=["Webadmin"]
)

class SafeUserUpdate(BaseModel):
    firstName: str | None = None
    lastName: str | None = None
    email: EmailStr | None = None
    emailVerified: bool | None = None
    enabled: bool | None = None


# 🧽 Limpiador de payload
def sanitize_user_payload(data: dict) -> dict:
    """
    Filters out any attribute that's malformed or unnecessary.
    Keeps attributes as str -> list[str]
    """
    if "attributes" in data:
        valid_attrs = {}
        for k, v in data["attributes"].items():
            if isinstance(v, list) and all(isinstance(i, str) for i in v):
                valid_attrs[k] = v
        if valid_attrs:
            data["attributes"] = valid_attrs
        else:
            data.pop("attributes", None)
    return data


@router.patch("/edit-user/{user_id}", summary="Safely update editable fields for a user")
def safe_update_user(
    user_id: str,
    request: SafeUserUpdate,
    current_user: dict = Depends(require_roles(["adminsuper"]))
):
    KEYCLOAK_URL = os.getenv("KEYCLOAK_URL")
    REALM_NAME = os.getenv("REALM_NAME")
    CLIENT_ID = os.getenv("CLIENT_ID")
    CLIENT_SECRET = os.getenv("CLIENT_SECRET")

    # 1. Get admin token
    token_resp = requests.post(
        f"{KEYCLOAK_URL}/realms/{REALM_NAME}/protocol/openid-connect/token",
        data={
            "grant_type": "client_credentials",
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    if token_resp.status_code != 200:
        raise HTTPException(status_code=401, detail="Failed to obtain admin token")

    token = token_resp.json()["access_token"]
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    # 2. Prepare fields to update
    data = request.dict(exclude_unset=True)
    if not data:
        raise HTTPException(status_code=400, detail="No fields provided for update.")

    data = sanitize_user_payload(data)

    # 3. Update via PUT (partial update style)
    update_resp = requests.put(
        f"{KEYCLOAK_URL}/admin/realms/{REALM_NAME}/users/{user_id}",
        headers=headers,
        json=data
    )
    if update_resp.status_code != 204:
        raise HTTPException(
            status_code=update_resp.status_code,
            detail=f"Failed to update user: {update_resp.text}"
        )

    return {"message": f"User '{user_id}' updated successfully."}

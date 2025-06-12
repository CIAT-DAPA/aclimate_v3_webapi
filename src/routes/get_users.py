from fastapi import APIRouter, Depends, HTTPException
import requests
import os
from dependencies.auth_dependencies import require_roles  # Your role-based validator

router = APIRouter(
    prefix="/users",
    tags=["Webadmin"]
)




@router.get("/get-users", summary="Get Webadmin users")
def get_users_with_webadminsimple(current_user: dict = Depends(require_roles(["adminsuper"]))):
        # Environment variables
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
    headers = {"Authorization": f"Bearer {token}"}

    # Step 2: Get client UUID by clientId
    clients_resp = requests.get(
        f"{KEYCLOAK_URL}/admin/realms/{REALM_NAME}/clients",
        headers=headers
    )
    if clients_resp.status_code != 200:
        raise HTTPException(status_code=clients_resp.status_code, detail="Failed to fetch clients")

    clients = clients_resp.json()
    client = next((c for c in clients if c["clientId"] == CLIENT_ID_NAME), None)
    if not client:
        raise HTTPException(status_code=404, detail=f"Client '{CLIENT_ID_NAME}' not found")
    client_uuid = client["id"]

    # Step 3: Get all users
    users_resp = requests.get(
        f"{KEYCLOAK_URL}/admin/realms/{REALM_NAME}/users",
        headers=headers
    )
    if users_resp.status_code != 200:
        raise HTTPException(status_code=users_resp.status_code, detail="Failed to fetch users")

    all_users = users_resp.json()
    filtered_users = []

    # Step 4: Filter users with the 'webadminsimple' client role
    for user in all_users:
        user_id = user["id"]
        roles_resp = requests.get(
            f"{KEYCLOAK_URL}/admin/realms/{REALM_NAME}/users/{user_id}/role-mappings/clients/{client_uuid}",
            headers=headers
        )
        if roles_resp.status_code != 200:
            continue

        roles = roles_resp.json()
        if any(role["name"] == "webadminsimple" for role in roles):
            filtered_users.append(user)

    return filtered_users

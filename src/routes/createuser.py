from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict
import os
import httpx
from dependencies.auth_dependencies import require_roles  # Tu validador existente

router = APIRouter(
    prefix="/users",
    tags=["manage_users"],
)

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
    credentials: List[Credential]  # ✅ aquí va la contraseña


async def get_admin_token():
    data = {
        "grant_type": "client_credentials",
        "client_id": CLIENT_ID,       
        "client_secret": CLIENT_SECRET,  
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    url = "http://localhost:8080/realms/aclimate/protocol/openid-connect/token"

    async with httpx.AsyncClient() as client:
        response = await client.post(url, data=data, headers=headers)

    if response.status_code != 200:
        print("Keycloak error:", response.text)
        raise HTTPException(status_code=401, detail="Credenciales inválidas o cliente no existe")
    print("Token obtenido:", response.json())
    return response.json()["access_token"]


@router.post("/crete-user", summary="create a keycloak user", )
async def crear_usuario(
    request: UserCreateRequest,
    current_user: dict = Depends(require_roles(["adminsuper"]))
):
    token = await get_admin_token()
    print(f"Token obtenido: {token}")

    user_payload = {
    "username": request.username,
    "email": request.email,
    "enabled": True,
    "emailVerified": request.emailVerified,
    "firstName": request.firstName or "",
    "lastName": request.lastName or "",
    "credentials": [cred.dict() for cred in request.credentials],

    "attributes": request.attributes or {}  # ✅ Solo se agrega si hay atributos
}

    
    async with httpx.AsyncClient() as client:
        # Crear el usuario
        create_resp = await client.post(
            f"{KEYCLOAK_URL}/admin/realms/{REALM_NAME}/users",
            headers={"Authorization": f"Bearer {token}"},
            json=user_payload,
        )
        if create_resp.status_code not in (201, 204):
            print("Error al crear usuario:", create_resp.text)  # 👈 agrega esto
            raise HTTPException(status_code=500, detail="Error al crear el usuario")


        # Obtener ID del nuevo usuario
        users_resp = await client.get(
            f"{KEYCLOAK_URL}/admin/realms/{REALM_NAME}/users?username={request.username}",
            headers={"Authorization": f"Bearer {token}"}
        )
        if users_resp.status_code != 200 or not users_resp.json():
            raise HTTPException(status_code=500, detail="No se pudo recuperar el ID del usuario")

        user_id = users_resp.json()[0]["id"]

        

    return {"message": "Usuario creado y roles asignados exitosamente con éxito", "user_id": user_id}
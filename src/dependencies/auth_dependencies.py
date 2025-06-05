from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError, ExpiredSignatureError
import requests
import os
from dotenv import load_dotenv
from typing import List

load_dotenv()

KEYCLOAK_URL = os.getenv("KEYCLOAK_URL")
REALM_NAME = os.getenv("REALM_NAME")
CLIENT_ID = os.getenv("CLIENT_ID")

JWKS_URL = f"{KEYCLOAK_URL}/realms/{REALM_NAME}/protocol/openid-connect/certs"
security = HTTPBearer()
JWKS = requests.get(JWKS_URL).json()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    token = credentials.credentials
    unverified_header = jwt.get_unverified_header(token)

    key = next((k for k in JWKS["keys"] if k["kid"] == unverified_header["kid"]), None)
    if not key:
        raise HTTPException(status_code=401, detail="Clave pública no encontrada")

    try:
        payload = jwt.decode(
            token,
            key,
            algorithms=[unverified_header["alg"]],
            audience="account",
            issuer=f"{KEYCLOAK_URL}/realms/{REALM_NAME}",
        )
        return payload

    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expirado")
    except JWTError as e:
        raise HTTPException(status_code=401, detail=f"Token inválido: {str(e)}")

def require_roles(required_roles: List[str]):
    def role_checker(current_user: dict = Depends(get_current_user)):
        client_roles = current_user.get("resource_access", {}).get(CLIENT_ID, {}).get("roles", [])

        if not any(role in client_roles for role in required_roles):
            raise HTTPException(
                status_code=403,
                detail=f"Acceso denegado. Se requieren roles: {required_roles}"
            )

        return current_user

    return role_checker

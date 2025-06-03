from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError, ExpiredSignatureError
import requests
import os
from dotenv import load_dotenv

load_dotenv()

KEYCLOAK_URL = os.getenv("KEYCLOAK_URL")
REALM_NAME = os.getenv("REALM_NAME")
CLIENT_ID = os.getenv("CLIENT_ID")

router = APIRouter(tags=["Authentication"])

JWKS_URL = f"{KEYCLOAK_URL}/realms/{REALM_NAME}/protocol/openid-connect/certs"

# Reutilizable para otras rutas
security = HTTPBearer()

def get_jwks():
    response = requests.get(JWKS_URL)
    if response.status_code != 200:
        raise Exception("Error fetching JWKS from Keycloak")
    return response.json()

JWKS = get_jwks()

@router.get("/token/validate", summary="Validate JWT token", description="Validate a JWT token against Keycloak's public keys.")
def validate_local_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    unverified_header = jwt.get_unverified_header(token)

    key = next((k for k in JWKS["keys"] if k["kid"] == unverified_header["kid"]), None)
    if not key:
        raise HTTPException(status_code=401, detail="Public key not found")

    try:
        payload = jwt.decode(
            token,
            key,
            algorithms=[unverified_header["alg"]],
            audience="account",
            issuer=f"{KEYCLOAK_URL}/realms/{REALM_NAME}",
        )
        return {"valid": True, "payload": payload}
    
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Expired token")
    except JWTError as e:
        raise HTTPException(status_code=401, detail=f"Invalid Token: {str(e)}")

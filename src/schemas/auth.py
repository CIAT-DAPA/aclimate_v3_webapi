from typing import Optional, List, Dict
from pydantic import BaseModel, EmailStr


class Credential(BaseModel):
    type: str = "password"
    value: str
    temporary: bool = False

    class Config:
        json_schema_extra = {
            "example": {
                "type": "password",
                "value": "SecurePass123!",
                "temporary": False
            }
        }


class UserCreateRequest(BaseModel):
    username: str
    email: str
    firstName: Optional[str] = ""
    lastName: Optional[str] = ""
    emailVerified: Optional[bool] = False
    enabled: Optional[bool] = True
    attributes: Optional[Dict[str, str]] = None
    credentials: List[Credential]

    class Config:
        json_schema_extra = {
            "example": {
                "username": "jdoe",
                "email": "jdoe@example.com",
                "firstName": "John",
                "lastName": "Doe",
                "emailVerified": False,
                "enabled": True,
                "attributes": {"country": "CO"},
                "credentials": [{"type": "password", "value": "SecurePass123!", "temporary": False}]
            }
        }


class CreateRoleRequest(BaseModel):
    name: str
    description: str | None = None
    composite: bool = False

    class Config:
        json_schema_extra = {
            "example": {
                "name": "webadminsimple",
                "description": "Basic web admin role",
                "composite": False
            }
        }


class DeleteUserRequest(BaseModel):
    user_id: str

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
            }
        }


class SafeUserUpdate(BaseModel):
    firstName: str | None = None
    lastName: str | None = None
    email: EmailStr | None = None
    emailVerified: bool | None = None
    enabled: bool | None = None

    class Config:
        json_schema_extra = {
            "example": {
                "firstName": "John",
                "lastName": "Doe",
                "email": "jdoe@example.com",
                "emailVerified": True,
                "enabled": True
            }
        }


class RoleAssignmentByIdRequest(BaseModel):
    user_id: str
    role_id: str

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
                "role_id": "f9e8d7c6-b5a4-3210-fedc-ba9876543210"
            }
        }


class RoleRemovalByIdRequest(BaseModel):
    user_id: str
    role_id: str

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
                "role_id": "f9e8d7c6-b5a4-3210-fedc-ba9876543210"
            }
        }

from datetime import datetime

from pydantic import BaseModel, EmailStr, ConfigDict


class CreateUserRequest(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: EmailStr
    is_active: bool
    is_verified: bool
    verified_at: datetime | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)



from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional


# ── Request schemas ──────────────────────────────────────────────────────────
# All request schemas use camelCase aliases to match the React frontend exactly.
# `populate_by_name=True` lets internal code also use snake_case field names.

class SignupRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    full_name: str = Field(alias="fullName")
    email: EmailStr
    password: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class UpdateProfileRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    profile_pic: str = Field(alias="profilePic")  # base64 data URI


class SendMessageRequest(BaseModel):
    text: Optional[str] = None
    image: Optional[str] = None  # base64 data URI


# ── Response schemas ─────────────────────────────────────────────────────────

class UserResponse(BaseModel):
    id: str
    full_name: str
    email: str
    profile_pic: str

    class Config:
        from_attributes = True


class MessageResponse(BaseModel):
    id: str
    sender_id: str
    receiver_id: str
    text: Optional[str] = None
    image: Optional[str] = None
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True

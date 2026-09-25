from beanie import Document
from pydantic import EmailStr, Field
from typing import Optional
from datetime import datetime, timezone


class User(Document):
    email: EmailStr
    full_name: str
    password: str
    profile_pic: str = ""
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "users"
        # mirrors Mongoose timestamps + unique email index
        indexes = ["email"]

    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "full_name": "John Doe",
                "password": "hashed_password",
                "profile_pic": "",
            }
        }

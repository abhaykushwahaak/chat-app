from beanie import Document, Link, PydanticObjectId
from pydantic import Field
from typing import Optional
from datetime import datetime, timezone


class Message(Document):
    sender_id: PydanticObjectId
    receiver_id: PydanticObjectId
    text: Optional[str] = None
    image: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "messages"

    class Config:
        json_schema_extra = {
            "example": {
                "sender_id": "60c72b2f9b1d4c3d88f1e8a1",
                "receiver_id": "60c72b2f9b1d4c3d88f1e8a2",
                "text": "Hello!",
                "image": None,
            }
        }

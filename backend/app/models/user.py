"""
User model for authentication and authorization.
"""
from datetime import datetime, timezone
from typing import Optional, Literal
from beanie import Document, Indexed
from pydantic import Field, EmailStr


class User(Document):
    email: Indexed(EmailStr, unique=True)  # type: ignore
    password_hash: str
    role: Literal["admin", "user"] = Field(default="user")

    # Profile information
    full_name: Optional[str] = None
    phone: Optional[str] = None

    # Account status
    is_active: bool = Field(default=True)
    is_verified: bool = Field(default=False)

    # Timestamps
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_login: Optional[datetime] = None

    # Company reference (for regular users)
    company_id: Optional[str] = None

    class Settings:
        name = "users"
        use_state_management = True

    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "role": "user",
                "full_name": "John Doe",
                "is_active": True
            }
        }

    def update_timestamp(self) -> None:
        self.updated_at = datetime.now(timezone.utc)

    def record_login(self) -> None:
        self.last_login = datetime.now(timezone.utc)
        self.update_timestamp()
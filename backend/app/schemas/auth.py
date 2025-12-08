"""
Authentication schemas for request/response validation.
"""
from typing import Optional, Literal
from pydantic import BaseModel, EmailStr, Field, field_validator
import re


class UserRegister(BaseModel):
    """Schema for user registration."""
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=100)
    full_name: Optional[str] = Field(None, min_length=2, max_length=100)
    role: Literal["admin", "user"] = "user"

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        """Validate password strength."""
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not re.search(r"\d", v):
            raise ValueError("Password must contain at least one digit")
        return v


class UserLogin(BaseModel):
    """Schema for user login."""
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """Schema for token response."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds


class TokenRefresh(BaseModel):
    """Schema for token refresh request."""
    refresh_token: str


class UserResponse(BaseModel):
    """Schema for user response (without sensitive data)."""
    id: str
    email: str
    role: str
    full_name: Optional[str] = None
    is_active: bool
    is_verified: bool
    company_id: Optional[str] = None
    created_at: str

    class Config:
        from_attributes = True


class AuthResponse(BaseModel):
    """Schema for authentication response."""
    token: TokenResponse
    user: UserResponse


class PasswordChange(BaseModel):
    """Schema for password change request."""
    current_password: str
    new_password: str = Field(..., min_length=8, max_length=100)

    @field_validator("new_password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        """Validate password strength."""
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not re.search(r"\d", v):
            raise ValueError("Password must contain at least one digit")
        return v


class MessageResponse(BaseModel):
    """Generic message response."""
    message: str
    success: bool = True
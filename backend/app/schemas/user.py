"""User schemas."""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class UserBase(BaseModel):
    """Common user fields shared across endpoints."""

    name: str = Field(..., min_length=1, max_length=150)
    email: EmailStr


class UserCreate(UserBase):
    """Schema for registering a new user."""

    password: str = Field(..., min_length=8, max_length=128)
    password_confirm: str = Field(..., min_length=8, max_length=128)

    @field_validator("password_confirm")
    @classmethod
    def passwords_match(cls, value: str, info) -> str:
        data = info.data
        if "password" in data and data["password"] != value:
            raise ValueError("Passwords do not match")
        return value


class UserUpdate(BaseModel):
    """Schema for updating the authenticated user's profile."""

    name: Optional[str] = Field(None, min_length=1, max_length=150)
    email: Optional[EmailStr] = None


class PasswordChange(BaseModel):
    """Schema for changing the password."""

    current_password: str = Field(..., min_length=8)
    new_password: str = Field(..., min_length=8, max_length=128)
    new_password_confirm: str = Field(..., min_length=8, max_length=128)

    @field_validator("new_password_confirm")
    @classmethod
    def passwords_match(cls, value: str, info) -> str:
        data = info.data
        if "new_password" in data and data["new_password"] != value:
            raise ValueError("Passwords do not match")
        return value


class UserRead(BaseModel):
    """User representation returned by the API. Excludes password_hash."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: EmailStr
    is_active: bool
    created_at: datetime
    updated_at: datetime

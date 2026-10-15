"""Authentication schemas (login request)."""
from __future__ import annotations

from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    """Login request body. Supports email + password."""

    email: EmailStr
    password: str = Field(..., min_length=1)


class LogoutResponse(BaseModel):
    message: str

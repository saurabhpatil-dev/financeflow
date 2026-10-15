"""Auth/token schemas."""
from __future__ import annotations

from pydantic import BaseModel


class Token(BaseModel):
    """JWT access token response."""

    access_token: str
    token_type: str = "bearer"
    expires_in: int


class TokenData(BaseModel):
    """Decoded token payload used internally."""

    user_id: int | None = None

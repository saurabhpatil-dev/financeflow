"""Security utilities: password hashing and JWT token management.

Uses ``bcrypt`` directly (rather than passlib) to avoid version-detection
issues with newer bcrypt releases.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

import bcrypt
from jose import JWTError, jwt


# bcrypt has a 72-byte limit on the password input. We hash longer
# passwords with sha256 first so users are not silently truncated.
_BCRYPT_MAX_BYTES = 72


def _normalize(password: str) -> bytes:
    data = password.encode("utf-8")
    if len(data) > _BCRYPT_MAX_BYTES:
        import hashlib

        data = hashlib.sha256(data).hexdigest().encode("ascii")
    return data


def hash_password(password: str) -> str:
    """Return a salted bcrypt hash of a plaintext password."""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(_normalize(password), salt).decode("ascii")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Constant-time comparison of a plaintext password against a hash."""
    try:
        return bcrypt.checkpw(_normalize(plain_password), hashed_password.encode("ascii"))
    except (ValueError, TypeError):
        return False


def create_access_token(
    subject: str | int,
    expires_minutes: Optional[int] = None,
    extra_claims: Optional[Dict[str, Any]] = None,
) -> str:
    """Create a signed JWT access token for the given subject (user id)."""
    from app.core.config import settings

    minutes = (
        expires_minutes
        if expires_minutes is not None
        else settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    expire = datetime.now(timezone.utc) + timedelta(minutes=minutes)
    payload: Dict[str, Any] = {
        "sub": str(subject),
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "type": "access",
    }
    if extra_claims:
        payload.update(extra_claims)
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_access_token(token: str) -> Dict[str, Any]:
    """Decode and validate a JWT. Raises JWTError on invalid/expired tokens."""
    from app.core.config import settings

    return jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])


def is_token_expired_error(exc: Exception) -> bool:
    return isinstance(exc, JWTError)

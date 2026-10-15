"""FastAPI dependencies for authentication and authorization."""
from __future__ import annotations

from fastapi import Depends, Header
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.exceptions import AuthenticationError
from app.db.dependencies import get_db
from app.models.user import User
from app.services.auth_service import AuthService


bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    authorization: str | None = Header(default=None),
) -> User:
    """Resolve the user authenticated by the Bearer token in the request.

    Raises AuthenticationError when the token is missing, malformed or no
    longer valid.
    """
    token: str | None = None
    if credentials is not None and credentials.credentials:
        token = credentials.credentials
    elif authorization and authorization.lower().startswith("bearer "):
        token = authorization.split(" ", 1)[1].strip()

    if not token:
        raise AuthenticationError("Missing authentication token", "missing_token")

    return AuthService(db).get_user_from_token(token)


def get_current_user_required(
    user: User = Depends(get_current_user),
) -> User:
    """Convenience alias used by protected endpoints."""
    return user

"""Authentication routes."""
from __future__ import annotations

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.dependencies import get_db
from app.models.user import User
from app.schemas.auth import LoginRequest, LogoutResponse
from app.schemas.token import Token
from app.schemas.user import UserCreate, UserRead
from app.services.auth_service import AuthService


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def register(payload: UserCreate, db: Session = Depends(get_db)) -> UserRead:
    """Register a new user account."""
    user = AuthService(db).register(payload)
    return UserRead.model_validate(user)


@router.post("/login", response_model=Token)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> Token:
    """Authenticate and return a JWT access token."""
    user, token, expires_in = AuthService(db).authenticate(payload)
    return Token(access_token=token, token_type="bearer", expires_in=expires_in)


@router.post("/logout", response_model=LogoutResponse)
def logout(
    _: User = Depends(get_current_user),
) -> LogoutResponse:
    """Stateless logout.

    The JWT is stateless, so the server does not maintain a session. The
    client is responsible for discarding the token. This endpoint exists so
    the frontend can call it and to allow future server-side revocation.
    """
    return LogoutResponse(message="Logged out successfully")


@router.get("/me", response_model=UserRead)
def me(current_user: User = Depends(get_current_user)) -> UserRead:
    """Return the currently authenticated user."""
    return UserRead.model_validate(current_user)

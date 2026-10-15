"""User profile management routes."""
from __future__ import annotations

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.dependencies import get_db
from app.models.user import User
from app.schemas.common import MessageResponse
from app.schemas.user import PasswordChange, UserRead, UserUpdate
from app.services.auth_service import AuthService


router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserRead)
def get_me(current_user: User = Depends(get_current_user)) -> UserRead:
    return UserRead.model_validate(current_user)


@router.put("/me", response_model=UserRead)
def update_me(
    payload: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> UserRead:
    user = AuthService(db).update_profile(current_user.id, payload)
    return UserRead.model_validate(user)


@router.put("/me/password", response_model=MessageResponse, status_code=status.HTTP_200_OK)
def change_password(
    payload: PasswordChange,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> MessageResponse:
    AuthService(db).change_password(current_user.id, payload)
    return MessageResponse(message="Password updated")

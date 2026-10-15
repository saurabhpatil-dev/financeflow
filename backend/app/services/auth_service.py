"""Authentication and user-management service."""
from __future__ import annotations

import logging

from sqlalchemy.orm import Session

from app.core.exceptions import (
    AuthenticationError,
    ConflictError,
    NotFoundError,
    ValidationError,
)
from app.core.security import create_access_token, hash_password, verify_password
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.auth import LoginRequest
from app.schemas.user import PasswordChange, UserCreate, UserUpdate

logger = logging.getLogger(__name__)


class AuthService:
    """Business logic for users and authentication."""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.users = UserRepository(db)

    # ---- Registration ----------------------------------------------------
    def register(self, payload: UserCreate) -> User:
        existing = self.users.get_by_email(payload.email)
        if existing is not None:
            raise ConflictError("An account with this email already exists", "email_taken")

        user = self.users.create(
            name=payload.name.strip(),
            email=payload.email.lower().strip(),
            password_hash=hash_password(payload.password),
        )
        # Seed the default categories for the new user so the app is usable
        # immediately after registration.
        from app.repositories.category_repository import CategoryRepository
        from app.services.defaults import default_categories

        CategoryRepository(self.db).bulk_create(default_categories(user.id))
        logger.info("Registered new user id=%s email=%s", user.id, user.email)
        return user

    # ---- Login -----------------------------------------------------------
    def authenticate(self, payload: LoginRequest) -> tuple[User, str, int]:
        user = self.users.get_by_email(payload.email.lower().strip())
        if user is None or not verify_password(payload.password, user.password_hash):
            raise AuthenticationError("Invalid email or password", "invalid_credentials")
        if not user.is_active:
            raise AuthenticationError("Account is disabled", "account_disabled")

        token = create_access_token(user.id)
        from app.core.config import settings

        return user, token, settings.ACCESS_TOKEN_EXPIRE_MINUTES

    # ---- Profile ---------------------------------------------------------
    def get_user(self, user_id: int) -> User:
        user = self.users.get_by_id(user_id)
        if user is None:
            raise NotFoundError("User not found", "user_not_found")
        return user

    def update_profile(self, user_id: int, payload: UserUpdate) -> User:
        user = self.get_user(user_id)

        if payload.email is not None:
            new_email = payload.email.lower().strip()
            if new_email != user.email:
                existing = self.users.get_by_email(new_email)
                if existing is not None and existing.id != user.id:
                    raise ConflictError("Email is already in use", "email_taken")
                user.email = new_email

        if payload.name is not None:
            user.name = payload.name.strip()

        return self.users.update(user)

    def change_password(self, user_id: int, payload: PasswordChange) -> User:
        user = self.get_user(user_id)
        if not verify_password(payload.current_password, user.password_hash):
            raise ValidationError("Current password is incorrect", "bad_password")
        if payload.current_password == payload.new_password:
            raise ValidationError("New password must differ from the current one", "same_password")
        return self.users.set_password_hash(user, hash_password(payload.new_password))

    # ---- Token decoding --------------------------------------------------
    def get_user_from_token(self, token: str) -> User:
        from app.core.exceptions import AuthenticationError
        from app.core.security import decode_access_token, is_token_expired_error

        try:
            payload = decode_access_token(token)
        except Exception as exc:
            if is_token_expired_error(exc):
                raise AuthenticationError("Token has expired", "token_expired")
            raise AuthenticationError("Could not validate credentials", "invalid_token")

        user_id_raw = payload.get("sub")
        if user_id_raw is None:
            raise AuthenticationError("Malformed token", "invalid_token")
        try:
            user_id = int(user_id_raw)
        except (TypeError, ValueError):
            raise AuthenticationError("Malformed token subject", "invalid_token")

        user = self.users.get_by_id(user_id)
        if user is None or not user.is_active:
            raise AuthenticationError("User not found or disabled", "user_not_found")
        return user

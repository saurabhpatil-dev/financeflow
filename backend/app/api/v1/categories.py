"""Category routes."""
from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.dependencies import get_db
from app.models.category import CategoryType
from app.models.user import User
from app.schemas.category import CategoryCreate, CategoryRead, CategoryUpdate
from app.schemas.common import MessageResponse
from app.services.category_service import CategoryService


router = APIRouter(prefix="/categories", tags=["categories"])


@router.get("", response_model=List[CategoryRead])
def list_categories(
    type: Optional[CategoryType] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> List[CategoryRead]:
    rows = CategoryService(db).list_for_user(current_user.id, type)
    return [CategoryRead.model_validate(c) for c in rows]


@router.post("", response_model=CategoryRead, status_code=status.HTTP_201_CREATED)
def create_category(
    payload: CategoryCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> CategoryRead:
    category = CategoryService(db).create(current_user.id, payload)
    return CategoryRead.model_validate(category)


@router.put("/{category_id}", response_model=CategoryRead)
def update_category(
    category_id: int,
    payload: CategoryUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> CategoryRead:
    category = CategoryService(db).update(current_user.id, category_id, payload)
    return CategoryRead.model_validate(category)


@router.delete("/{category_id}", response_model=MessageResponse)
def delete_category(
    category_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> MessageResponse:
    CategoryService(db).delete(current_user.id, category_id)
    return MessageResponse(message="Category deleted")

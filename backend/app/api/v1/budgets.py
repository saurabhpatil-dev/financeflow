"""Budget routes."""
from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.dependencies import get_db
from app.models.user import User
from app.schemas.budget import BudgetCreate, BudgetRead, BudgetUpdate, BudgetWithProgress
from app.schemas.common import MessageResponse
from app.services.budget_service import BudgetService


router = APIRouter(prefix="/budgets", tags=["budgets"])


def _to_read(budget) -> BudgetRead:
    category_name = budget.category.name if budget.category is not None else None
    return BudgetRead(
        id=budget.id,
        user_id=budget.user_id,
        category_id=budget.category_id,
        category_name=category_name,
        year=budget.year,
        month=budget.month,
        amount=budget.amount,
        created_at=budget.created_at,
        updated_at=budget.updated_at,
    )


@router.get("", response_model=List[BudgetWithProgress])
def list_budgets(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> List[BudgetWithProgress]:
    return BudgetService(db).list_for_user(current_user.id)


@router.post("", response_model=BudgetWithProgress, status_code=status.HTTP_201_CREATED)
def create_budget(
    payload: BudgetCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> BudgetWithProgress:
    budget = BudgetService(db).create(current_user.id, payload)
    return BudgetService(db)._with_progress(budget)


@router.put("/{budget_id}", response_model=BudgetWithProgress)
def update_budget(
    budget_id: int,
    payload: BudgetUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> BudgetWithProgress:
    budget = BudgetService(db).update(current_user.id, budget_id, payload)
    return BudgetService(db)._with_progress(budget)


@router.delete("/{budget_id}", response_model=MessageResponse)
def delete_budget(
    budget_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> MessageResponse:
    BudgetService(db).delete(current_user.id, budget_id)
    return MessageResponse(message="Budget deleted")

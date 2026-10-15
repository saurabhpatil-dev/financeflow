"""Transaction routes."""
from __future__ import annotations

import math
from typing import List, Optional

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.dependencies import get_db
from app.models.transaction import TransactionType
from app.models.user import User
from app.schemas.common import PageMeta, PaginatedResponse
from app.schemas.transaction import (
    TransactionCreate,
    TransactionRead,
    TransactionUpdate,
)
from app.services.transaction_service import TransactionService


router = APIRouter(prefix="/transactions", tags=["transactions"])


def _to_read(transaction, category_name: Optional[str]) -> TransactionRead:
    return TransactionRead(
        id=transaction.id,
        user_id=transaction.user_id,
        type=transaction.type,
        amount=transaction.amount,
        category_id=transaction.category_id,
        category_name=category_name,
        description=transaction.description,
        transaction_date=transaction.transaction_date,
        created_at=transaction.created_at,
        updated_at=transaction.updated_at,
    )


def _read_with_category(txn) -> TransactionRead:
    name = txn.category.name if txn.category is not None else None
    return _to_read(txn, name)


@router.get("", response_model=PaginatedResponse[TransactionRead])
def list_transactions(
    type: Optional[TransactionType] = None,
    category_id: Optional[int] = None,
    search: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    sort_by: str = "transaction_date",
    sort_order: str = "desc",
    page: int = 1,
    page_size: int = 20,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> PaginatedResponse[TransactionRead]:
    """List the current user's transactions with filtering, search and pagination."""
    from datetime import date as date_type

    def _parse(value: Optional[str]) -> Optional[date_type]:
        if value is None or value == "":
            return None
        return date_type.fromisoformat(value)

    rows, total = TransactionService(db).list_for_user(
        current_user.id,
        type_filter=type,
        category_id=category_id,
        search=search,
        start_date=_parse(start_date),
        end_date=_parse(end_date),
        sort_by=sort_by,
        sort_order=sort_order,
        page=page,
        page_size=page_size,
    )
    items: List[TransactionRead] = []
    # Eagerly fetch category names to avoid N+1.
    category_ids = {txn.category_id for txn in rows if txn.category_id is not None}
    category_names: dict[int, str] = {}
    if category_ids:
        from app.repositories.category_repository import CategoryRepository

        for cat in CategoryRepository(db).list_for_user(current_user.id):
            category_names[cat.id] = cat.name

    for txn in rows:
        items.append(
            _to_read(
                txn,
                category_names.get(txn.category_id) if txn.category_id else None,
            )
        )

    total_pages = math.ceil(total / page_size) if total else 0
    return PaginatedResponse[TransactionRead](
        items=items,
        meta=PageMeta(page=page, page_size=page_size, total=total, total_pages=total_pages),
    )


@router.post("", response_model=TransactionRead, status_code=status.HTTP_201_CREATED)
def create_transaction(
    payload: TransactionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> TransactionRead:
    txn = TransactionService(db).create(current_user.id, payload)
    return _read_with_category(txn)


@router.get("/{transaction_id}", response_model=TransactionRead)
def get_transaction(
    transaction_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> TransactionRead:
    txn = TransactionService(db).get_for_user(transaction_id, current_user.id)
    return _read_with_category(txn)


@router.put("/{transaction_id}", response_model=TransactionRead)
def update_transaction(
    transaction_id: int,
    payload: TransactionUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> TransactionRead:
    txn = TransactionService(db).update(current_user.id, transaction_id, payload)
    return _read_with_category(txn)


@router.delete("/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_transaction(
    transaction_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    TransactionService(db).delete(current_user.id, transaction_id)

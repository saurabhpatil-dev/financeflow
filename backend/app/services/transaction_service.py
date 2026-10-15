"""Transaction service."""
from __future__ import annotations

from datetime import date
from typing import Optional, Sequence, Tuple

from sqlalchemy.orm import Session

from app.core.exceptions import BusinessRuleError, NotFoundError, ValidationError
from app.models.transaction import Transaction, TransactionType
from app.repositories.category_repository import CategoryRepository
from app.repositories.transaction_repository import TransactionRepository
from app.schemas.transaction import TransactionCreate, TransactionUpdate


class TransactionService:
    """Business logic for transactions."""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.transactions = TransactionRepository(db)
        self.categories = CategoryRepository(db)

    def _validate_category(
        self,
        user_id: int,
        category_id: Optional[int],
        type_: TransactionType,
    ) -> None:
        if category_id is None:
            return
        category = self.categories.get_for_user(category_id, user_id)
        if category is None:
            raise NotFoundError("Category not found", "category_not_found")
        if category.type != type_:
            raise BusinessRuleError(
                f"Category '{category.name}' is for {category.type.value} but the "
                f"transaction type is {type_.value}",
                "category_type_mismatch",
            )

    def create(self, user_id: int, payload: TransactionCreate) -> Transaction:
        self._validate_category(user_id, payload.category_id, payload.type)
        if payload.transaction_date > date.today():
            raise ValidationError(
                "Transaction date cannot be in the future",
                "future_date",
            )
        transaction = Transaction(
            user_id=user_id,
            type=payload.type,
            amount=payload.amount,
            category_id=payload.category_id,
            description=payload.description,
            transaction_date=payload.transaction_date,
        )
        return self.transactions.create(transaction)

    def get_for_user(self, transaction_id: int, user_id: int) -> Transaction:
        transaction = self.transactions.get_for_user(transaction_id, user_id)
        if transaction is None:
            raise NotFoundError("Transaction not found", "transaction_not_found")
        return transaction

    def list_for_user(
        self,
        user_id: int,
        *,
        type_filter: Optional[TransactionType] = None,
        category_id: Optional[int] = None,
        search: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        sort_by: str = "transaction_date",
        sort_order: str = "desc",
        page: int = 1,
        page_size: int = 20,
    ) -> Tuple[Sequence[Transaction], int]:
        if start_date and end_date and start_date > end_date:
            raise ValidationError(
                "start_date cannot be after end_date",
                "invalid_date_range",
            )
        return self.transactions.list_for_user(
            user_id,
            type_filter=type_filter,
            category_id=category_id,
            search=search,
            start_date=start_date,
            end_date=end_date,
            sort_by=sort_by,
            sort_order=sort_order,
            page=page,
            page_size=page_size,
        )

    def update(
        self,
        user_id: int,
        transaction_id: int,
        payload: TransactionUpdate,
    ) -> Transaction:
        transaction = self.get_for_user(transaction_id, user_id)

        type_ = payload.type if payload.type is not None else transaction.type
        category_id = (
            payload.category_id if payload.category_id is not None else transaction.category_id
        )
        if payload.type is not None or payload.category_id is not None:
            self._validate_category(user_id, category_id, type_)

        new_date = (
            payload.transaction_date
            if payload.transaction_date is not None
            else transaction.transaction_date
        )
        if new_date > date.today():
            raise ValidationError(
                "Transaction date cannot be in the future",
                "future_date",
            )

        if payload.type is not None:
            transaction.type = type_
        if payload.amount is not None:
            transaction.amount = payload.amount
        if payload.category_id is not None:
            transaction.category_id = payload.category_id
        if payload.description is not None:
            transaction.description = payload.description
        if payload.transaction_date is not None:
            transaction.transaction_date = payload.transaction_date

        return self.transactions.update(transaction)

    def delete(self, user_id: int, transaction_id: int) -> None:
        transaction = self.get_for_user(transaction_id, user_id)
        self.transactions.delete(transaction)

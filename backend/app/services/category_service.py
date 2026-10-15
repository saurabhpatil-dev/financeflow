"""Category service."""
from __future__ import annotations

from typing import Optional, Sequence

from sqlalchemy.orm import Session

from app.core.exceptions import BusinessRuleError, ConflictError, NotFoundError
from app.models.category import Category, CategoryType
from app.repositories.category_repository import CategoryRepository
from app.repositories.transaction_repository import TransactionRepository
from app.schemas.category import CategoryCreate, CategoryUpdate


class CategoryService:
    """Business logic for categories."""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.categories = CategoryRepository(db)
        self.transactions = TransactionRepository(db)

    def list_for_user(
        self,
        user_id: int,
        type_filter: Optional[CategoryType] = None,
    ) -> Sequence[Category]:
        return self.categories.list_for_user(user_id, type_filter)

    def create(self, user_id: int, payload: CategoryCreate) -> Category:
        name = payload.name.strip()
        if self.categories.exists_by_name(user_id, name, payload.type):
            raise ConflictError(
                "A category with this name and type already exists",
                "category_exists",
            )
        return self.categories.create(
            user_id=user_id,
            name=name,
            type_=payload.type,
            color=payload.color,
            icon=payload.icon,
        )

    def update(self, user_id: int, category_id: int, payload: CategoryUpdate) -> Category:
        category = self.categories.get_for_user(category_id, user_id)
        if category is None:
            raise NotFoundError("Category not found", "category_not_found")

        new_name = payload.name.strip() if payload.name is not None else category.name
        new_type = payload.type if payload.type is not None else category.type

        if (
            (new_name != category.name or new_type != category.type)
            and self.categories.exists_by_name(user_id, new_name, new_type, exclude_id=category.id)
        ):
            raise ConflictError(
                "A category with this name and type already exists",
                "category_exists",
            )

        category.name = new_name
        category.type = new_type
        if payload.color is not None:
            category.color = payload.color
        if payload.icon is not None:
            category.icon = payload.icon
        return self.categories.update(category)

    def delete(self, user_id: int, category_id: int) -> None:
        category = self.categories.get_for_user(category_id, user_id)
        if category is None:
            raise NotFoundError("Category not found", "category_not_found")

        # Foreign key is ondelete=CASCADE so transactions are removed, which is
        # rarely desirable. Block deletion if any transactions reference it.
        from sqlalchemy import select
        from app.models.transaction import Transaction

        count_stmt = select(Transaction.id).where(Transaction.category_id == category_id).limit(1)
        if self.db.execute(count_stmt).first() is not None:
            raise BusinessRuleError(
                "Cannot delete a category that is referenced by transactions. "
                "Reassign or delete those transactions first.",
                "category_in_use",
            )
        self.categories.delete(category)

    def get_or_default(
        self,
        user_id: int,
        category_id: Optional[int],
        type_: CategoryType,
    ) -> Optional[Category]:
        """Resolve a category id ensuring it belongs to the user.

        Returns ``None`` if category_id is None (transactions allow null
        category). Raises NotFoundError if the id does not belong to the user.
        """
        if category_id is None:
            return None
        category = self.categories.get_for_user(category_id, user_id)
        if category is None:
            raise NotFoundError("Category not found", "category_not_found")
        return category

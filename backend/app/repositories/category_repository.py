"""Category repository."""
from __future__ import annotations

from typing import List, Optional, Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.category import Category, CategoryType


class CategoryRepository:
    """Encapsulates database access for categories."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_id(self, category_id: int) -> Optional[Category]:
        return self.db.get(Category, category_id)

    def get_for_user(self, category_id: int, user_id: int) -> Optional[Category]:
        stmt = select(Category).where(
            Category.id == category_id, Category.user_id == user_id
        )
        return self.db.execute(stmt).scalar_one_or_none()

    def list_for_user(
        self,
        user_id: int,
        type_filter: Optional[CategoryType] = None,
    ) -> Sequence[Category]:
        stmt = select(Category).where(Category.user_id == user_id)
        if type_filter is not None:
            stmt = stmt.where(Category.type == type_filter)
        stmt = stmt.order_by(Category.type.asc(), Category.name.asc())
        return self.db.execute(stmt).scalars().all()

    def create(
        self,
        *,
        user_id: int,
        name: str,
        type_: CategoryType,
        color: Optional[str] = None,
        icon: Optional[str] = None,
    ) -> Category:
        category = Category(
            user_id=user_id,
            name=name,
            type=type_,
            color=color,
            icon=icon,
        )
        self.db.add(category)
        self.db.commit()
        self.db.refresh(category)
        return category

    def update(self, category: Category) -> Category:
        self.db.add(category)
        self.db.commit()
        self.db.refresh(category)
        return category

    def delete(self, category: Category) -> None:
        self.db.delete(category)
        self.db.commit()

    def exists_by_name(
        self, user_id: int, name: str, type_: CategoryType, exclude_id: Optional[int] = None
    ) -> bool:
        stmt = select(Category.id).where(
            Category.user_id == user_id,
            Category.name == name,
            Category.type == type_,
        )
        if exclude_id is not None:
            stmt = stmt.where(Category.id != exclude_id)
        return self.db.execute(stmt).first() is not None

    def bulk_create(self, categories: List[Category]) -> None:
        self.db.add_all(categories)
        self.db.commit()

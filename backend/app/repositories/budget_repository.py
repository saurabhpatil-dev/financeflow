"""Budget repository."""
from __future__ import annotations

from typing import Optional, Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.budget import Budget


class BudgetRepository:
    """Encapsulates database access for budgets."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def get_for_user(self, budget_id: int, user_id: int) -> Optional[Budget]:
        stmt = select(Budget).where(Budget.id == budget_id, Budget.user_id == user_id)
        return self.db.execute(stmt).scalar_one_or_none()

    def list_for_user(self, user_id: int) -> Sequence[Budget]:
        stmt = select(Budget).where(Budget.user_id == user_id).order_by(
            Budget.year.desc(), Budget.month.desc()
        )
        return self.db.execute(stmt).scalars().all()

    def list_for_period(
        self, user_id: int, year: int, month: int
    ) -> Sequence[Budget]:
        stmt = select(Budget).where(
            Budget.user_id == user_id, Budget.year == year, Budget.month == month
        )
        return self.db.execute(stmt).scalars().all()

    def get_for_category_period(
        self, user_id: int, category_id: int, year: int, month: int
    ) -> Optional[Budget]:
        stmt = select(Budget).where(
            Budget.user_id == user_id,
            Budget.category_id == category_id,
            Budget.year == year,
            Budget.month == month,
        )
        return self.db.execute(stmt).scalar_one_or_none()

    def create(self, budget: Budget) -> Budget:
        self.db.add(budget)
        self.db.commit()
        self.db.refresh(budget)
        return budget

    def update(self, budget: Budget) -> Budget:
        self.db.add(budget)
        self.db.commit()
        self.db.refresh(budget)
        return budget

    def delete(self, budget: Budget) -> None:
        self.db.delete(budget)
        self.db.commit()

    def exists_for_category_period(
        self,
        user_id: int,
        category_id: int,
        year: int,
        month: int,
        exclude_id: Optional[int] = None,
    ) -> bool:
        stmt = select(Budget.id).where(
            Budget.user_id == user_id,
            Budget.category_id == category_id,
            Budget.year == year,
            Budget.month == month,
        )
        if exclude_id is not None:
            stmt = stmt.where(Budget.id != exclude_id)
        return self.db.execute(stmt).first() is not None

"""Budget service."""
from __future__ import annotations

import calendar
from datetime import date
from decimal import Decimal
from typing import List

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.exceptions import BusinessRuleError, ConflictError, NotFoundError
from app.models.budget import Budget
from app.models.category import Category, CategoryType
from app.models.transaction import Transaction, TransactionType
from app.repositories.budget_repository import BudgetRepository
from app.repositories.category_repository import CategoryRepository
from app.repositories.transaction_repository import TransactionRepository
from app.schemas.budget import BudgetCreate, BudgetUpdate, BudgetWithProgress


class BudgetService:
    """Business logic for budgets."""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.budgets = BudgetRepository(db)
        self.categories = CategoryRepository(db)
        self.transactions = TransactionRepository(db)

    def _resolve_category(self, user_id: int, category_id: int) -> Category:
        category = self.categories.get_for_user(category_id, user_id)
        if category is None:
            raise NotFoundError("Category not found", "category_not_found")
        if category.type != CategoryType.expense:
            raise BusinessRuleError(
                "Budgets can only be set for expense categories",
                "budget_income_category",
            )
        return category

    def create(self, user_id: int, payload: BudgetCreate) -> Budget:
        self._resolve_category(user_id, payload.category_id)
        if self.budgets.exists_for_category_period(
            user_id, payload.category_id, payload.year, payload.month
        ):
            raise ConflictError(
                "A budget already exists for this category in this period",
                "budget_exists",
            )
        budget = Budget(
            user_id=user_id,
            category_id=payload.category_id,
            year=payload.year,
            month=payload.month,
            amount=payload.amount,
        )
        return self.budgets.create(budget)

    def update(self, user_id: int, budget_id: int, payload: BudgetUpdate) -> Budget:
        budget = self.budgets.get_for_user(budget_id, user_id)
        if budget is None:
            raise NotFoundError("Budget not found", "budget_not_found")
        budget.amount = payload.amount
        return self.budgets.update(budget)

    def delete(self, user_id: int, budget_id: int) -> None:
        budget = self.budgets.get_for_user(budget_id, user_id)
        if budget is None:
            raise NotFoundError("Budget not found", "budget_not_found")
        self.budgets.delete(budget)

    def list_for_user(self, user_id: int) -> List[BudgetWithProgress]:
        budgets = self.budgets.list_for_user(user_id)
        return [self._with_progress(b) for b in budgets]

    def _with_progress(self, budget: Budget) -> BudgetWithProgress:
        category = budget.category if budget.category is not None else self.categories.get_for_user(
            budget.category_id, budget.user_id
        )
        category_name = category.name if category is not None else "Unknown"

        last_day = calendar.monthrange(budget.year, budget.month)[1]
        period_start = date(budget.year, budget.month, 1)
        period_end = date(budget.year, budget.month, last_day)

        spent = self.transactions.totals_for_user(
            budget.user_id,
            type_=TransactionType.expense,
            start_date=period_start,
            end_date=period_end,
        )
        # Restrict to this category
        category_spent_stmt = select(
            func.coalesce(func.sum(Transaction.amount), 0)
        ).where(
            Transaction.user_id == budget.user_id,
            Transaction.type == TransactionType.expense,
            Transaction.category_id == budget.category_id,
            Transaction.transaction_date >= period_start,
            Transaction.transaction_date <= period_end,
        )
        spent = Decimal(str(self.db.execute(category_spent_stmt).scalar_one()))

        remaining = budget.amount - spent
        percent_used = float((spent / budget.amount * 100)) if budget.amount > 0 else 0.0

        if percent_used >= 100:
            status = "exceeded"
        elif percent_used >= 80:
            status = "warning"
        else:
            status = "ok"

        return BudgetWithProgress(
            id=budget.id,
            user_id=budget.user_id,
            category_id=budget.category_id,
            category_name=category_name,
            year=budget.year,
            month=budget.month,
            amount=budget.amount,
            spent=spent,
            remaining=remaining,
            percent_used=round(percent_used, 2),
            status=status,
        )

"""Dashboard service: aggregates summary data for the home screen."""
from __future__ import annotations

import calendar
from datetime import date, timedelta
from decimal import Decimal
from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.transaction import TransactionType
from app.repositories.category_repository import CategoryRepository
from app.repositories.transaction_repository import TransactionRepository
from app.schemas.dashboard import (
    CategoryBreakdown,
    DashboardSummary,
    MonthlyPoint,
    RecentTransaction,
)


class DashboardService:
    """Compute dashboard aggregates scoped to the requesting user."""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.transactions = TransactionRepository(db)
        self.categories = CategoryRepository(db)

    def summary(self, user_id: int, *, today: Optional[date] = None) -> DashboardSummary:
        today = today or date.today()
        month_start = today.replace(day=1)
        month_end = month_start.replace(
            day=calendar.monthrange(today.year, today.month)[1]
        )
        prev_month_end = month_start - timedelta(days=1)
        prev_month_start = prev_month_end.replace(day=1)

        total_income = self.transactions.totals_for_user(
            user_id, type_=TransactionType.income
        )
        total_expense = self.transactions.totals_for_user(
            user_id, type_=TransactionType.expense
        )
        current_balance = total_income - total_expense

        monthly_income = self.transactions.totals_for_user(
            user_id, type_=TransactionType.income, start_date=month_start, end_date=month_end
        )
        monthly_expense = self.transactions.totals_for_user(
            user_id, type_=TransactionType.expense, start_date=month_start, end_date=month_end
        )
        monthly_balance = monthly_income - monthly_expense

        prev_income = self.transactions.totals_for_user(
            user_id,
            type_=TransactionType.income,
            start_date=prev_month_start,
            end_date=prev_month_end,
        )
        prev_expense = self.transactions.totals_for_user(
            user_id,
            type_=TransactionType.expense,
            start_date=prev_month_start,
            end_date=prev_month_end,
        )

        income_change = _pct_change(prev_income, monthly_income)
        expense_change = _pct_change(prev_expense, monthly_expense)

        breakdown_raw = self.transactions.category_breakdown(
            user_id, type_=TransactionType.expense,
            start_date=month_start, end_date=month_end,
        )
        expense_breakdown = _breakdown(breakdown_raw, monthly_expense)

        trend_start = (today.replace(day=1) - timedelta(days=365)).replace(day=1)
        trend_rows = self.transactions.monthly_aggregates(
            user_id, start_date=trend_start, end_date=month_end
        )
        # Fill missing months with zeros for a smooth chart.
        monthly_trend = _fill_missing_months(trend_rows, trend_start, month_end)

        recent = self.transactions.recent_for_user(user_id, limit=5)
        recent_transactions: List[RecentTransaction] = []
        for txn in recent:
            recent_transactions.append(
                RecentTransaction(
                    id=txn.id,
                    type=txn.type.value,
                    amount=txn.amount,
                    category_name=txn.category.name if txn.category else None,
                    description=txn.description,
                    transaction_date=txn.transaction_date,
                )
            )

        return DashboardSummary(
            total_income=total_income,
            total_expense=total_expense,
            current_balance=current_balance,
            monthly_income=monthly_income,
            monthly_expense=monthly_expense,
            monthly_balance=monthly_balance,
            income_change_pct=income_change,
            expense_change_pct=expense_change,
            recent_transactions=recent_transactions,
            expense_breakdown=expense_breakdown,
            monthly_trend=monthly_trend,
        )


def _pct_change(prev: Decimal, current: Decimal) -> Optional[float]:
    if prev == 0:
        return None if current == 0 else 100.0
    return round(float((current - prev) / prev * 100), 2)


def _breakdown(rows: List[dict], total: Decimal) -> List[CategoryBreakdown]:
    safe_total = total if total > 0 else Decimal("1")
    out: List[CategoryBreakdown] = []
    for row in rows:
        out.append(
            CategoryBreakdown(
                category_id=row["category_id"],
                category_name=row["category_name"] or "Uncategorized",
                amount=row["amount"],
                percentage=round(float(row["amount"] / safe_total * 100), 2),
                transaction_count=row["transaction_count"],
            )
        )
    return out


def _fill_missing_months(rows: List[dict], start: date, end: date) -> List[MonthlyPoint]:
    by_month = {row["month"]: row for row in rows}
    points: List[MonthlyPoint] = []
    current = start.replace(day=1)
    while current <= end:
        key = current.strftime("%Y-%m")
        row = by_month.get(key)
        income = Decimal(str(row["income"])) if row else Decimal("0")
        expense = Decimal(str(row["expense"])) if row else Decimal("0")
        points.append(
            MonthlyPoint(
                month=key,
                income=income,
                expense=expense,
                balance=income - expense,
            )
        )
        # Advance one month
        year = current.year + (1 if current.month == 12 else 0)
        month = 1 if current.month == 12 else current.month + 1
        current = date(year, month, 1)
    return points

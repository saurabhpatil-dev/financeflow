"""Reports service: financial analytics for charts and exports."""
from __future__ import annotations

import calendar
from datetime import date
from decimal import Decimal
from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.transaction import TransactionType
from app.repositories.transaction_repository import TransactionRepository
from app.schemas.reports import (
    CategoryReport,
    CategoryReportItem,
    MonthlyReport,
    MonthlyReportItem,
    SummaryReport,
    TrendPoint,
    TrendReport,
)


class ReportsService:
    """Compute financial reports for a user over an arbitrary date range."""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.transactions = TransactionRepository(db)

    # ---- Monthly report -------------------------------------------------
    def monthly_report(
        self,
        user_id: int,
        *,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> MonthlyReport:
        start, end = self._resolve_range(start_date, end_date, default_months=12)
        # Always start the per-month grouping from the 1st of the start month.
        start = start.replace(day=1)
        end = end.replace(day=calendar.monthrange(end.year, end.month)[1])

        rows = self.transactions.monthly_aggregates(user_id, start_date=start, end_date=end)
        items: List[MonthlyReportItem] = []
        total_income = Decimal("0")
        total_expense = Decimal("0")

        for row in rows:
            income = Decimal(str(row["income"]))
            expense = Decimal(str(row["expense"]))
            balance = income - expense
            savings_rate = round(float(balance / income * 100), 2) if income > 0 else 0.0
            items.append(
                MonthlyReportItem(
                    month=row["month"],
                    income=income,
                    expense=expense,
                    balance=balance,
                    savings_rate=savings_rate,
                )
            )
            total_income += income
            total_expense += expense

        total_balance = total_income - total_expense
        avg_savings_rate = (
            round(float(total_balance / total_income * 100), 2) if total_income > 0 else 0.0
        )

        return MonthlyReport(
            items=items,
            total_income=total_income,
            total_expense=total_expense,
            total_balance=total_balance,
            average_savings_rate=avg_savings_rate,
        )

    # ---- Category report -------------------------------------------------
    def category_report(
        self,
        user_id: int,
        *,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> CategoryReport:
        start, end = self._resolve_range(start_date, end_date, default_months=1)

        expense_rows = self.transactions.category_breakdown(
            user_id, type_=TransactionType.expense, start_date=start, end_date=end
        )
        income_rows = self.transactions.category_breakdown(
            user_id, type_=TransactionType.income, start_date=start, end_date=end
        )

        total_expense = sum((r["amount"] for r in expense_rows), Decimal("0"))
        total_income = sum((r["amount"] for r in income_rows), Decimal("0"))

        items: List[CategoryReportItem] = []
        for row in expense_rows:
            denom = total_expense if total_expense > 0 else Decimal("1")
            items.append(
                CategoryReportItem(
                    category_id=row["category_id"],
                    category_name=row["category_name"] or "Uncategorized",
                    type="expense",
                    total=row["amount"],
                    percentage=round(float(row["amount"] / denom * 100), 2),
                    transaction_count=row["transaction_count"],
                )
            )
        for row in income_rows:
            denom = total_income if total_income > 0 else Decimal("1")
            items.append(
                CategoryReportItem(
                    category_id=row["category_id"],
                    category_name=row["category_name"] or "Uncategorized",
                    type="income",
                    total=row["amount"],
                    percentage=round(float(row["amount"] / denom * 100), 2),
                    transaction_count=row["transaction_count"],
                )
            )

        return CategoryReport(items=items)

    # ---- Trend report ---------------------------------------------------
    def trend_report(
        self,
        user_id: int,
        *,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> TrendReport:
        start, end = self._resolve_range(start_date, end_date, default_months=6)
        start = start.replace(day=1)
        end = end.replace(day=calendar.monthrange(end.year, end.month)[1])

        rows = self.transactions.monthly_aggregates(user_id, start_date=start, end_date=end)
        points: List[TrendPoint] = []
        by_month = {row["month"]: row for row in rows}

        current = start
        while current <= end:
            key = current.strftime("%Y-%m")
            row = by_month.get(key)
            income = Decimal(str(row["income"])) if row else Decimal("0")
            expense = Decimal(str(row["expense"])) if row else Decimal("0")
            points.append(
                TrendPoint(period=key, income=income, expense=expense, balance=income - expense)
            )
            year = current.year + (1 if current.month == 12 else 0)
            month = 1 if current.month == 12 else current.month + 1
            current = date(year, month, 1)

        return TrendReport(granularity="monthly", points=points)

    # ---- Summary report --------------------------------------------------
    def summary_report(
        self,
        user_id: int,
        *,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> SummaryReport:
        start, end = self._resolve_range(start_date, end_date, default_months=1)
        start = start.replace(day=1)
        end = end.replace(day=calendar.monthrange(end.year, end.month)[1])

        income = self.transactions.totals_for_user(
            user_id, type_=TransactionType.income, start_date=start, end_date=end
        )
        expense = self.transactions.totals_for_user(
            user_id, type_=TransactionType.expense, start_date=start, end_date=end
        )
        balance = income - expense
        savings_rate = round(float(balance / income * 100), 2) if income > 0 else 0.0

        rows = self.transactions.category_breakdown(
            user_id, type_=TransactionType.expense, start_date=start, end_date=end
        )
        highest_name: Optional[str] = None
        highest_amount: Optional[Decimal] = None
        if rows:
            highest = rows[0]
            highest_name = highest["category_name"] or "Uncategorized"
            highest_amount = highest["amount"]

        count_stmt_total = sum((r["transaction_count"] for r in rows), 0)

        return SummaryReport(
            start_date=start,
            end_date=end,
            income=income,
            expense=expense,
            balance=balance,
            savings_rate=savings_rate,
            highest_expense_category=highest_name,
            highest_expense_amount=highest_amount,
            transaction_count=int(count_stmt_total),
        )

    # ---- Helpers ---------------------------------------------------------
    def _resolve_range(
        self,
        start_date: Optional[date],
        end_date: Optional[date],
        *,
        default_months: int,
    ) -> tuple[date, date]:
        today = date.today()
        if start_date is None and end_date is None:
            end = today
            start_month = today.month - default_months
            start_year = today.year
            while start_month <= 0:
                start_month += 12
                start_year -= 1
            start = date(start_year, start_month, 1)
            return start, end

        if start_date is None:
            start_date = end_date.replace(day=1)
        if end_date is None:
            end_date = start_date.replace(
                day=calendar.monthrange(start_date.year, start_date.month)[1]
            )
        if start_date > end_date:
            start_date, end_date = end_date, start_date
        return start_date, end_date

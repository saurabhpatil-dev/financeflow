"""Reports schemas."""
from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel


class DateRangeParams(BaseModel):
    """Optional date range filter used by report endpoints."""

    start_date: Optional[date] = None
    end_date: Optional[date] = None


class MonthlyReportItem(BaseModel):
    month: str  # YYYY-MM
    income: Decimal
    expense: Decimal
    balance: Decimal
    savings_rate: float


class MonthlyReport(BaseModel):
    items: List[MonthlyReportItem]
    total_income: Decimal
    total_expense: Decimal
    total_balance: Decimal
    average_savings_rate: float


class CategoryReportItem(BaseModel):
    category_id: int | None
    category_name: str
    type: str
    total: Decimal
    percentage: float
    transaction_count: int


class CategoryReport(BaseModel):
    items: List[CategoryReportItem]


class TrendPoint(BaseModel):
    period: str
    income: Decimal
    expense: Decimal
    balance: Decimal


class TrendReport(BaseModel):
    granularity: str  # "monthly" | "daily"
    points: List[TrendPoint]


class SummaryReport(BaseModel):
    start_date: date
    end_date: date
    income: Decimal
    expense: Decimal
    balance: Decimal
    savings_rate: float
    highest_expense_category: Optional[str] = None
    highest_expense_amount: Optional[Decimal] = None
    transaction_count: int

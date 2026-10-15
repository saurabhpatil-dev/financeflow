"""Dashboard summary schemas."""
from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import List

from pydantic import BaseModel


class CategoryBreakdown(BaseModel):
    category_id: int | None
    category_name: str
    amount: Decimal
    percentage: float
    transaction_count: int


class MonthlyPoint(BaseModel):
    month: str  # YYYY-MM
    income: Decimal
    expense: Decimal
    balance: Decimal


class RecentTransaction(BaseModel):
    id: int
    type: str
    amount: Decimal
    category_name: str | None
    description: str | None
    transaction_date: date


class DashboardSummary(BaseModel):
    total_income: Decimal
    total_expense: Decimal
    current_balance: Decimal
    monthly_income: Decimal
    monthly_expense: Decimal
    monthly_balance: Decimal
    income_change_pct: float | None
    expense_change_pct: float | None
    recent_transactions: List[RecentTransaction]
    expense_breakdown: List[CategoryBreakdown]
    monthly_trend: List[MonthlyPoint]

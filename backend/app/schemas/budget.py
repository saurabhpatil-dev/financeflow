"""Budget schemas."""
from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field, field_validator

from app.schemas.common import ORMModel


class BudgetBase(BaseModel):
    category_id: int
    year: int = Field(..., ge=2000, le=2100)
    month: int = Field(..., ge=1, le=12)
    amount: Decimal = Field(..., gt=0, max_digits=14, decimal_places=2)

    @field_validator("amount")
    @classmethod
    def _round_amount(cls, value: Decimal) -> Decimal:
        return value.quantize(Decimal("0.01"))


class BudgetCreate(BudgetBase):
    pass


class BudgetUpdate(BaseModel):
    amount: Decimal = Field(..., gt=0, max_digits=14, decimal_places=2)

    @field_validator("amount")
    @classmethod
    def _round_amount(cls, value: Decimal) -> Decimal:
        return value.quantize(Decimal("0.01"))


class BudgetRead(ORMModel):
    id: int
    user_id: int
    category_id: int
    category_name: Optional[str] = None
    year: int
    month: int
    amount: Decimal
    created_at: datetime
    updated_at: datetime


class BudgetWithProgress(ORMModel):
    """A budget plus the current spending against it."""

    id: int
    user_id: int
    category_id: int
    category_name: str
    year: int
    month: int
    amount: Decimal
    spent: Decimal
    remaining: Decimal
    percent_used: float
    status: str  # "ok" | "warning" | "exceeded"

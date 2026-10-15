"""Transaction schemas."""
from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.transaction import TransactionType


class TransactionBase(BaseModel):
    type: TransactionType
    amount: Decimal = Field(..., gt=0, max_digits=14, decimal_places=2)
    category_id: Optional[int] = None
    description: Optional[str] = Field(None, max_length=500)
    transaction_date: date

    @field_validator("amount")
    @classmethod
    def _round_amount(cls, value: Decimal) -> Decimal:
        # Normalize precision before storage.
        return value.quantize(Decimal("0.01"))


class TransactionCreate(TransactionBase):
    pass


class TransactionUpdate(BaseModel):
    type: Optional[TransactionType] = None
    amount: Optional[Decimal] = Field(None, gt=0, max_digits=14, decimal_places=2)
    category_id: Optional[int] = None
    description: Optional[str] = Field(None, max_length=500)
    transaction_date: Optional[date] = None

    @field_validator("amount")
    @classmethod
    def _round_amount(cls, value: Optional[Decimal]) -> Optional[Decimal]:
        if value is None:
            return value
        return value.quantize(Decimal("0.01"))


class TransactionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    type: TransactionType
    amount: Decimal
    category_id: Optional[int] = None
    category_name: Optional[str] = None
    description: Optional[str] = None
    transaction_date: date
    created_at: datetime
    updated_at: datetime


class TransactionFilters(BaseModel):
    """Query parameters supported by the transactions list endpoint."""

    type: Optional[TransactionType] = None
    category_id: Optional[int] = None
    search: Optional[str] = Field(None, max_length=200)
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    sort_by: Optional[str] = Field(
        "transaction_date",
        pattern="^(transaction_date|amount|created_at)$",
    )
    sort_order: Optional[str] = Field("desc", pattern="^(asc|desc)$")
    page: int = Field(1, ge=1)
    page_size: int = Field(20, ge=1, le=200)


class TransactionListParams(TransactionFilters):
    pass

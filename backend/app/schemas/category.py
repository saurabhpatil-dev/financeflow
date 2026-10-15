"""Category schemas."""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from app.models.category import CategoryType


class CategoryBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=80)
    type: CategoryType
    color: Optional[str] = Field(None, max_length=32)
    icon: Optional[str] = Field(None, max_length=64)


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=80)
    type: Optional[CategoryType] = None
    color: Optional[str] = Field(None, max_length=32)
    icon: Optional[str] = Field(None, max_length=64)


class CategoryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    name: str
    type: CategoryType
    color: Optional[str] = None
    icon: Optional[str] = None
    created_at: datetime
    updated_at: datetime

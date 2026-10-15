"""Shared Pydantic schemas used across the API."""
from __future__ import annotations

from typing import Generic, List, TypeVar

from pydantic import BaseModel, Field


T = TypeVar("T")


class ORMModel(BaseModel):
    """Base that enables ORM->Pydantic conversion via from_attributes."""

    model_config = {"from_attributes": True}


class PageMeta(BaseModel):
    """Pagination metadata returned alongside page results."""

    page: int = Field(..., ge=1)
    page_size: int = Field(..., ge=1, le=200)
    total: int = Field(..., ge=0)
    total_pages: int = Field(..., ge=0)


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response wrapper."""

    items: List[T]
    meta: PageMeta


class MessageResponse(BaseModel):
    """Simple message response for delete/update endpoints."""

    message: str

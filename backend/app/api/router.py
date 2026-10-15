"""Aggregates all v1 routers under a single prefix."""
from __future__ import annotations

from fastapi import APIRouter

from app.api.v1 import auth, budgets, categories, dashboard, reports, transactions, users


api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(transactions.router)
api_router.include_router(categories.router)
api_router.include_router(budgets.router)
api_router.include_router(dashboard.router)
api_router.include_router(reports.router)

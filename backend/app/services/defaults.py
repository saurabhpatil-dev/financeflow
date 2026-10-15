"""Default categories seeded on first user creation/registration."""
from __future__ import annotations

from typing import List, Tuple

from app.models.category import Category, CategoryType


def default_categories(user_id: int) -> List[Category]:
    """Return the default categories for a freshly-registered user."""
    categories: List[Category] = []
    for name, color, icon in _DEFAULT_INCOME:
        categories.append(
            Category(
                user_id=user_id,
                name=name,
                type=CategoryType.income,
                color=color,
                icon=icon,
            )
        )
    for name, color, icon in _DEFAULT_EXPENSE:
        categories.append(
            Category(
                user_id=user_id,
                name=name,
                type=CategoryType.expense,
                color=color,
                icon=icon,
            )
        )
    return categories


_DEFAULT_INCOME: List[Tuple[str, str, str]] = [
    ("Salary", "#22c55e", "briefcase"),
    ("Freelance", "#10b981", "laptop"),
    ("Business", "#0ea5e9", "store"),
    ("Investment", "#8b5cf6", "trending-up"),
    ("Other", "#64748b", "plus"),
]

_DEFAULT_EXPENSE: List[Tuple[str, str, str]] = [
    ("Food", "#ef4444", "utensils"),
    ("Transport", "#f59e0b", "car"),
    ("Shopping", "#ec4899", "shopping-bag"),
    ("Bills", "#3b82f6", "file-text"),
    ("Rent", "#6366f1", "home"),
    ("Healthcare", "#14b8a6", "heart"),
    ("Education", "#a855f7", "book"),
    ("Entertainment", "#f97316", "film"),
    ("Travel", "#06b6d4", "plane"),
    ("Other", "#64748b", "plus"),
]

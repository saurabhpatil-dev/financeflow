"""Pydantic schemas package."""
from app.schemas.auth import LoginRequest, LogoutResponse
from app.schemas.budget import (
    BudgetCreate,
    BudgetRead,
    BudgetUpdate,
    BudgetWithProgress,
)
from app.schemas.category import CategoryCreate, CategoryRead, CategoryUpdate
from app.schemas.common import (
    MessageResponse,
    PaginatedResponse,
    PageMeta,
)
from app.schemas.dashboard import (
    CategoryBreakdown,
    DashboardSummary,
    MonthlyPoint,
    RecentTransaction,
)
from app.schemas.reports import (
    CategoryReport,
    CategoryReportItem,
    DateRangeParams,
    MonthlyReport,
    MonthlyReportItem,
    SummaryReport,
    TrendPoint,
    TrendReport,
)
from app.schemas.token import Token, TokenData
from app.schemas.transaction import (
    TransactionCreate,
    TransactionFilters,
    TransactionRead,
    TransactionUpdate,
)
from app.schemas.user import (
    PasswordChange,
    UserCreate,
    UserRead,
    UserUpdate,
)

__all__ = [
    "LoginRequest",
    "LogoutResponse",
    "BudgetCreate",
    "BudgetRead",
    "BudgetUpdate",
    "BudgetWithProgress",
    "CategoryCreate",
    "CategoryRead",
    "CategoryUpdate",
    "MessageResponse",
    "PaginatedResponse",
    "PageMeta",
    "CategoryBreakdown",
    "DashboardSummary",
    "MonthlyPoint",
    "RecentTransaction",
    "CategoryReport",
    "CategoryReportItem",
    "DateRangeParams",
    "MonthlyReport",
    "MonthlyReportItem",
    "SummaryReport",
    "TrendPoint",
    "TrendReport",
    "Token",
    "TokenData",
    "TransactionCreate",
    "TransactionFilters",
    "TransactionRead",
    "TransactionUpdate",
    "PasswordChange",
    "UserCreate",
    "UserRead",
    "UserUpdate",
]

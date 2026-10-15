"""Reports routes."""
from __future__ import annotations

from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.dependencies import get_db
from app.models.user import User
from app.schemas.reports import (
    CategoryReport,
    MonthlyReport,
    SummaryReport,
    TrendReport,
)
from app.services.reports_service import ReportsService


router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/monthly", response_model=MonthlyReport)
def monthly_report(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> MonthlyReport:
    return ReportsService(db).monthly_report(
        current_user.id, start_date=start_date, end_date=end_date
    )


@router.get("/categories", response_model=CategoryReport)
def category_report(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> CategoryReport:
    return ReportsService(db).category_report(
        current_user.id, start_date=start_date, end_date=end_date
    )


@router.get("/trends", response_model=TrendReport)
def trend_report(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> TrendReport:
    return ReportsService(db).trend_report(
        current_user.id, start_date=start_date, end_date=end_date
    )


@router.get("/summary", response_model=SummaryReport)
def summary_report(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> SummaryReport:
    return ReportsService(db).summary_report(
        current_user.id, start_date=start_date, end_date=end_date
    )

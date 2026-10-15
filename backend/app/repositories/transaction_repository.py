"""Transaction repository."""
from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import List, Optional, Sequence, Tuple

from sqlalchemy import asc, desc, func, or_, select
from sqlalchemy.orm import Session

from app.models.transaction import Transaction, TransactionType


class TransactionRepository:
    """Encapsulates database access for transactions."""

    def __init__(self, db: Session) -> None:
        self.db = db

    # ---- CRUD -----------------------------------------------------------
    def get_for_user(self, transaction_id: int, user_id: int) -> Optional[Transaction]:
        stmt = select(Transaction).where(
            Transaction.id == transaction_id, Transaction.user_id == user_id
        )
        return self.db.execute(stmt).scalar_one_or_none()

    def create(self, transaction: Transaction) -> Transaction:
        self.db.add(transaction)
        self.db.commit()
        self.db.refresh(transaction)
        return transaction

    def update(self, transaction: Transaction) -> Transaction:
        self.db.add(transaction)
        self.db.commit()
        self.db.refresh(transaction)
        return transaction

    def delete(self, transaction: Transaction) -> None:
        self.db.delete(transaction)
        self.db.commit()

    # ---- Listing / filtering ---------------------------------------------
    def list_for_user(
        self,
        user_id: int,
        *,
        type_filter: Optional[TransactionType] = None,
        category_id: Optional[int] = None,
        search: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        sort_by: str = "transaction_date",
        sort_order: str = "desc",
        page: int = 1,
        page_size: int = 20,
    ) -> Tuple[Sequence[Transaction], int]:
        stmt = select(Transaction).where(Transaction.user_id == user_id)

        if type_filter is not None:
            stmt = stmt.where(Transaction.type == type_filter)
        if category_id is not None:
            stmt = stmt.where(Transaction.category_id == category_id)
        if start_date is not None:
            stmt = stmt.where(Transaction.transaction_date >= start_date)
        if end_date is not None:
            stmt = stmt.where(Transaction.transaction_date <= end_date)
        if search:
            pattern = f"%{search}%"
            stmt = stmt.where(or_(Transaction.description.ilike(pattern),))

        sort_column = getattr(Transaction, sort_by, Transaction.transaction_date)
        stmt = stmt.order_by(
            desc(sort_column) if sort_order.lower() == "desc" else asc(sort_column),
            desc(Transaction.id),
        )

        count_stmt = select(func.count()).select_from(
            stmt.order_by(None).subquery()
        )
        total = self.db.execute(count_stmt).scalar_one()

        offset = (page - 1) * page_size
        rows = self.db.execute(stmt.offset(offset).limit(page_size)).scalars().all()
        return rows, int(total)

    # ---- Aggregations ----------------------------------------------------
    def totals_for_user(
        self,
        user_id: int,
        *,
        type_: TransactionType,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> Decimal:
        stmt = select(func.coalesce(func.sum(Transaction.amount), 0)).where(
            Transaction.user_id == user_id, Transaction.type == type_
        )
        if start_date is not None:
            stmt = stmt.where(Transaction.transaction_date >= start_date)
        if end_date is not None:
            stmt = stmt.where(Transaction.transaction_date <= end_date)
        return Decimal(str(self.db.execute(stmt).scalar_one()))

    def category_breakdown(
        self,
        user_id: int,
        *,
        type_: TransactionType = TransactionType.expense,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> List[dict]:
        """Return per-category aggregates for the user."""
        from app.models.category import Category

        total_expr = func.sum(Transaction.amount).label("total")
        stmt = (
            select(
                Transaction.category_id,
                Category.name.label("category_name"),
                total_expr,
                func.count(Transaction.id).label("count"),
            )
            .join(Category, Category.id == Transaction.category_id, isouter=True)
            .where(Transaction.user_id == user_id, Transaction.type == type_)
            .group_by(Transaction.category_id, Category.name)
            .order_by(total_expr.desc())
        )
        if start_date is not None:
            stmt = stmt.where(Transaction.transaction_date >= start_date)
        if end_date is not None:
            stmt = stmt.where(Transaction.transaction_date <= end_date)

        rows = self.db.execute(stmt).all()
        return [
            {
                "category_id": row.category_id,
                "category_name": row.category_name,
                "amount": Decimal(str(row.total or 0)),
                "transaction_count": int(row.count or 0),
            }
            for row in rows
        ]

    def monthly_aggregates(
        self,
        user_id: int,
        *,
        start_date: date,
        end_date: date,
    ) -> List[dict]:
        """Return per-month income/expense aggregates as a list of dicts.

        Uses dialect-agnostic SQL (``extract`` + ``case``) so the same query
        works on MySQL and SQLite (the latter is used by the test-suite).
        """
        from sqlalchemy import case, extract

        year_col = extract("year", Transaction.transaction_date).label("year")
        month_col = extract("month", Transaction.transaction_date).label("month")
        income_sum = func.coalesce(
            func.sum(
                case(
                    (Transaction.type == TransactionType.income, Transaction.amount),
                    else_=0,
                )
            ),
            0,
        ).label("income")
        expense_sum = func.coalesce(
            func.sum(
                case(
                    (Transaction.type == TransactionType.expense, Transaction.amount),
                    else_=0,
                )
            ),
            0,
        ).label("expense")
        stmt = (
            select(year_col, month_col, income_sum, expense_sum)
            .where(
                Transaction.user_id == user_id,
                Transaction.transaction_date >= start_date,
                Transaction.transaction_date <= end_date,
            )
            .group_by(year_col, month_col)
            .order_by(year_col.asc(), month_col.asc())
        )
        rows = self.db.execute(stmt).all()
        return [
            {
                "month": f"{int(row.year):04d}-{int(row.month):02d}",
                "income": Decimal(str(row.income or 0)),
                "expense": Decimal(str(row.expense or 0)),
            }
            for row in rows
        ]

    def recent_for_user(self, user_id: int, limit: int = 5) -> Sequence[Transaction]:
        stmt = (
            select(Transaction)
            .where(Transaction.user_id == user_id)
            .order_by(desc(Transaction.transaction_date), desc(Transaction.id))
            .limit(limit)
        )
        return self.db.execute(stmt).scalars().all()

    def delete_all_for_user(self, user_id: int) -> None:
        self.db.execute(
            Transaction.__table__.delete().where(Transaction.user_id == user_id)
        )
        self.db.commit()

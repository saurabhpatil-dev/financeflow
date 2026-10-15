"""Budget ORM model."""
from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Numeric, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.mixins import TimestampMixin

if TYPE_CHECKING:
    from app.models.category import Category
    from app.models.user import User


class Budget(Base, TimestampMixin):
    """A monthly budget for a specific expense category.

    The combination of (user_id, category_id, year, month) is unique so a
    user can have exactly one budget per category per month.
    """

    __tablename__ = "budgets"
    __table_args__ = (
        UniqueConstraint(
            "user_id", "category_id", "year", "month", name="uq_user_category_period"
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    category_id: Mapped[int] = mapped_column(
        ForeignKey("categories.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    year: Mapped[int] = mapped_column(nullable=False, index=True)
    month: Mapped[int] = mapped_column(nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="budgets")
    category: Mapped["Category"] = relationship("Category")  # no back_populates: budgets
    # should not be eagerly loaded from a category.

    def __repr__(self) -> str:  # pragma: no cover - trivial
        return (
            f"<Budget id={self.id} user={self.user_id} category={self.category_id} "
            f"{self.year}-{self.month:02d} amount={self.amount}>"
        )

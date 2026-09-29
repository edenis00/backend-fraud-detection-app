from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import DateTime, Enum as SAEnum, String, func, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.enums import UserRole
from app.database.base import Base

if TYPE_CHECKING:
    from app.cards.models import Card
    from app.departments.models import Department
    from app.transactions.models import Transaction
    from app.reports.models import Report


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    full_name: Mapped[str] = mapped_column(String(150), nullable=False)
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False,
    )
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(
        SAEnum(UserRole, name="user_role"),
        default=UserRole.ANALYST,
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    department_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("departments.id"), index=True, nullable=True
    )

    department: Mapped["Department | None"] = relationship(
        "Department",
        back_populates="users",
    )

    assigned_cards: Mapped[list["Card"]] = relationship(
        "Card",
        back_populates="assigned_user",
    )

    transactions: Mapped[list["Transaction"]] = relationship(
        "Transaction",
        back_populates="user",
    )

    reports: Mapped[list["Report"]] = relationship(
        "Report",
        back_populates="generated_by_user",
    )
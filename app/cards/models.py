from datetime import date, datetime
from typing import Optional
from sqlalchemy import Date, DateTime, Integer, String, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class Card(Base):
    __tablename__ = "cards"

    id: Mapped[int] = mapped_column(primary_key=True)
    card_reference: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    masked_card_number: Mapped[str] = mapped_column(String(32), nullable=False)
    department_id: Mapped[int] = mapped_column(ForeignKey("departments.id"), index=True, nullable=False)
    assigned_user_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"), index=True, nullable=True)
    card_type: Mapped[Optional[str]] = mapped_column(String(32))
    issue_date: Mapped[Optional[date]] = mapped_column(Date)
    expiry_date: Mapped[Optional[date]] = mapped_column(Date)
    status: Mapped[str] = mapped_column(String(32), default="active", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    department: Mapped["Department"] = relationship("Department", back_populates="cards")
    assigned_user: Mapped[Optional["User"]] = relationship("User", back_populates="assigned_cards")

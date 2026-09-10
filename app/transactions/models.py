from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum as SAEnum, ForeignKey, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.enums import FraudStatus, TransactionStatus
from app.database.base import Base

if TYPE_CHECKING:
    from app.alerts.models import FraudAlert
    from app.users.models import User


class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(primary_key=True)
    transaction_reference: Mapped[str] = mapped_column(
        String(64),
        unique=True,
        index=True,
        nullable=False,
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        index=True,
        nullable=False,
    )
    card_reference: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False)
    transaction_type: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    location: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    transaction_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        index=True,
        nullable=False,
    )
    status: Mapped[TransactionStatus] = mapped_column(
        SAEnum(TransactionStatus, name="transaction_status"),
        default=TransactionStatus.PROCESSED,
        nullable=False,
    )
    fraud_status: Mapped[FraudStatus] = mapped_column(
        SAEnum(FraudStatus, name="fraud_status"),
        default=FraudStatus.NORMAL,
        index=True,
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    user: Mapped["User"] = relationship(
        "User",
        back_populates="transactions",
    )
    alerts: Mapped[list["FraudAlert"]] = relationship(
        "FraudAlert",
        back_populates="transaction",
        cascade="all, delete-orphan",
    )
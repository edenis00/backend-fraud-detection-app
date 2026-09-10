from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum as SAEnum, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.enums import AlertStatus
from app.database.base import Base

if TYPE_CHECKING:
    from app.transactions.models import Transaction


class FraudAlert(Base):
    __tablename__ = "fraud_alerts"

    id: Mapped[int] = mapped_column(primary_key=True)
    transaction_id: Mapped[int] = mapped_column(
        ForeignKey("transactions.id"),
        index=True,
        nullable=False,
    )
    rule_name: Mapped[str] = mapped_column(String(120), nullable=False)
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    alert_status: Mapped[AlertStatus] = mapped_column(
        SAEnum(AlertStatus, name="alert_status"),
        default=AlertStatus.NEW,
        index=True,
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    transaction: Mapped["Transaction"] = relationship(
        "Transaction",
        back_populates="alerts",
    )
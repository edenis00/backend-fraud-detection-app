from datetime import datetime
from decimal import Decimal
from typing import Optional
from sqlalchemy import DateTime, Integer, String, Text, Numeric, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class FraudRule(Base):
    __tablename__ = "fraud_rules"

    id: Mapped[int] = mapped_column(primary_key=True)
    rule_code: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    # The initial migration created this column as `name`; preserve that
    # database name while exposing the domain-consistent `rule_name` field.
    rule_name: Mapped[str] = mapped_column("name", String(150), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    threshold: Mapped[Optional[Decimal]] = mapped_column(Numeric(15, 2))
    severity: Mapped[str] = mapped_column(String(32), default="medium", nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="active", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

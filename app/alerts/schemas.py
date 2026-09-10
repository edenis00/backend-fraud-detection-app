from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict

from app.core.enums import AlertStatus, FraudStatus


class AlertTransactionResponse(BaseModel):
    id: int
    transaction_reference: str
    amount: Decimal
    transaction_type: str
    location: str
    transaction_date: datetime
    fraud_status: FraudStatus

    model_config = ConfigDict(from_attributes=True)


class FraudAlertResponse(BaseModel):
    id: int
    rule_name: str
    reason: str
    alert_status: AlertStatus
    created_at: datetime
    reviewed_at: datetime | None
    transaction: AlertTransactionResponse

    model_config = ConfigDict(from_attributes=True)


class FraudAlertListResponse(BaseModel):
    items: list[FraudAlertResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class FraudAlertUpdate(BaseModel):
    alert_status: AlertStatus
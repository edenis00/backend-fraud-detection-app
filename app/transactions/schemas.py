from datetime import datetime
from decimal import Decimal
import re

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.core.enums import FraudStatus, TransactionStatus


class TransactionCreate(BaseModel):
    transaction_reference: str = Field(min_length=3, max_length=64)
    card_reference: str = Field(min_length=4, max_length=64)
    amount: Decimal = Field(gt=0, max_digits=15, decimal_places=2)
    transaction_type: str = Field(min_length=2, max_length=100)
    location: str = Field(min_length=2, max_length=255)
    transaction_date: datetime

    model_config = ConfigDict(str_strip_whitespace=True)

    @field_validator("card_reference")
    @classmethod
    def reject_full_card_numbers(cls, value: str) -> str:
        digits_only = re.sub(r"\D", "", value)

        if re.fullmatch(r"\d{13,19}", digits_only):
            raise ValueError(
                "Use a masked card number or internal card reference, not a full card number."
            )

        return value


class TransactionResponse(BaseModel):
    id: int
    transaction_reference: str
    card_reference: str
    amount: Decimal
    transaction_type: str
    location: str
    transaction_date: datetime
    status: TransactionStatus
    fraud_status: FraudStatus
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TransactionProcessResponse(BaseModel):
    transaction: TransactionResponse
    alert_generated: bool
    alert_ids: list[int]
    triggered_rules: list[str]


class TransactionListResponse(BaseModel):
    items: list[TransactionResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
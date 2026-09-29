from typing import Optional
from pydantic import BaseModel
from datetime import date, datetime


class CardBase(BaseModel):
    card_reference: str
    masked_card_number: str
    department_id: int
    assigned_user_id: Optional[int] = None
    card_type: Optional[str] = None
    issue_date: Optional[date] = None
    expiry_date: Optional[date] = None
    status: str = "active"


class CardCreate(CardBase):
    pass


class CardUpdate(BaseModel):
    masked_card_number: Optional[str] = None
    department_id: Optional[int] = None
    assigned_user_id: Optional[int] = None
    card_type: Optional[str] = None
    issue_date: Optional[date] = None
    expiry_date: Optional[date] = None
    status: Optional[str] = None


class CardResponse(CardBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

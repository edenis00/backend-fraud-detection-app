from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


class CardCreate(BaseModel):
    last_four: str = Field(pattern=r"^\d{4}$")
    department_id: int
    assigned_user_id: int | None = None
    card_type: str | None = None
    issue_date: date | None = None
    expiry_date: date | None = None
    status: str = "active"

    model_config = ConfigDict(str_strip_whitespace=True)


class CardUpdate(BaseModel):
    department_id: int | None = None
    assigned_user_id: int | None = None
    card_type: str | None = None
    issue_date: date | None = None
    expiry_date: date | None = None
    status: str | None = None


class CardResponse(BaseModel):
    id: int
    card_reference: str
    masked_card_number: str
    department_id: int
    assigned_user_id: int | None
    card_type: str | None
    issue_date: date | None
    expiry_date: date | None
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
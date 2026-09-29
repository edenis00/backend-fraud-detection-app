from typing import Optional
from pydantic import BaseModel
from datetime import datetime


class FraudRuleBase(BaseModel):
    rule_code: str
    rule_name: str
    description: Optional[str] = None
    threshold: Optional[float] = None
    severity: str = "medium"
    status: str = "active"


class FraudRuleCreate(FraudRuleBase):
    pass


class FraudRuleUpdate(BaseModel):
    rule_code: Optional[str] = None
    rule_name: Optional[str] = None
    description: Optional[str] = None
    threshold: Optional[float] = None
    severity: Optional[str] = None
    status: Optional[str] = None


class FraudRuleResponse(FraudRuleBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

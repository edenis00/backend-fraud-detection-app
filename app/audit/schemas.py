from typing import Optional
from pydantic import BaseModel
from datetime import datetime


class AuditLogCreate(BaseModel):
    user_id: int
    action: str
    entity_type: str
    entity_id: Optional[int] = None
    details: Optional[dict] = None


class AuditLogResponse(BaseModel):
    id: int
    user_id: int
    action: str
    entity_type: str
    entity_id: Optional[int]
    details: Optional[dict]
    timestamp: datetime

    class Config:
        from_attributes = True

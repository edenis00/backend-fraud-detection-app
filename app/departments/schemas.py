from typing import Optional
from pydantic import BaseModel
from datetime import datetime


class DepartmentBase(BaseModel):
    department_code: str
    name: str
    description: Optional[str] = None
    status: str = "active"


class DepartmentCreate(DepartmentBase):
    pass


class DepartmentUpdate(BaseModel):
    department_code: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None


class DepartmentResponse(DepartmentBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

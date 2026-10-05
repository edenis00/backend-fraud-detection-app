from pydantic import BaseModel, ConfigDict, EmailStr, Field
from decimal import Decimal
from app.core.enums import UserRole


class AdminUserCreate(BaseModel):
    full_name: str = Field(min_length=2, max_length=150)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    role: UserRole = UserRole.ANALYST
    department_id: int | None = None

    model_config = ConfigDict(str_strip_whitespace=True)


class AdminRoleUpdate(BaseModel):
    role: UserRole


class AmountThresholdUpdate(BaseModel):
    threshold: Decimal = Field(gt=0, max_digits=15, decimal_places=2)


class AmountThresholdResponse(BaseModel):
    threshold: Decimal
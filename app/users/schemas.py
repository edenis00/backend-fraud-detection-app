from datetime import datetime

from pydantic import ConfigDict, EmailStr
from pydantic import BaseModel

from app.core.enums import UserRole


class UserResponse(BaseModel):
    id: int
    full_name: str
    email: EmailStr
    role: UserRole
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
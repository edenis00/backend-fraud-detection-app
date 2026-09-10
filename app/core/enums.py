from enum import Enum


class UserRole(str, Enum):
    ADMIN = "admin"
    ANALYST = "analyst"
    USER = "user"


class TransactionStatus(str, Enum):
    PROCESSED = "processed"


class FraudStatus(str, Enum):
    NORMAL = "normal"
    SUSPICIOUS = "suspicious"


class AlertStatus(str, Enum):
    NEW = "new"
    UNDER_REVIEW = "under_review"
    REVIEWED = "reviewed"
    RESOLVED = "resolved"
from datetime import date
from decimal import Decimal

from pydantic import BaseModel

from app.core.enums import AlertStatus


class DashboardSummaryResponse(BaseModel):
    total_transactions: int
    normal_transactions: int
    suspicious_transactions: int
    fraud_alert_count: int
    total_transaction_value: Decimal


class TransactionTrendResponse(BaseModel):
    date: date
    transaction_count: int
    total_value: Decimal
    suspicious_count: int


class DistributionResponse(BaseModel):
    category: str
    transaction_count: int
    total_value: Decimal
    suspicious_count: int


class AlertStatusCountResponse(BaseModel):
    alert_status: AlertStatus
    count: int


class FraudRuleCountResponse(BaseModel):
    rule_name: str
    count: int


class FraudStatisticsResponse(BaseModel):
    normal_transactions: int
    suspicious_transactions: int
    total_alerts: int
    alerts_by_status: list[AlertStatusCountResponse]
    alerts_by_rule: list[FraudRuleCountResponse]
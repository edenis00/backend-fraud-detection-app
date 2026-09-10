from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.analysis.schemas import (
    DashboardSummaryResponse,
    DistributionResponse,
    FraudStatisticsResponse,
    TransactionTrendResponse,
)
from app.analysis.service import (
    get_dashboard_summary,
    get_distribution,
    get_fraud_statistics,
    get_transaction_trends,
)
from app.auth.dependencies import get_current_user
from app.database.session import get_db
from app.users.models import User

router = APIRouter(prefix="/api/analysis", tags=["analysis"])

DatabaseSession = Annotated[Session, Depends(get_db)]


@router.get("/summary", response_model=DashboardSummaryResponse)
def get_summary(
    db: DatabaseSession,
    current_user: User = Depends(get_current_user),
) -> DashboardSummaryResponse:
    return get_dashboard_summary(db, current_user)


@router.get("/trends", response_model=list[TransactionTrendResponse])
def get_trends(
    db: DatabaseSession,
    current_user: User = Depends(get_current_user),
    start_date: datetime | None = None,
    end_date: datetime | None = None,
) -> list[TransactionTrendResponse]:
    return get_transaction_trends(db, current_user, start_date, end_date)


@router.get("/by-type", response_model=list[DistributionResponse])
def get_by_type(
    db: DatabaseSession,
    current_user: User = Depends(get_current_user),
) -> list[DistributionResponse]:
    return get_distribution(db, current_user, "transaction_type")


@router.get("/by-location", response_model=list[DistributionResponse])
def get_by_location(
    db: DatabaseSession,
    current_user: User = Depends(get_current_user),
) -> list[DistributionResponse]:
    return get_distribution(db, current_user, "location")


@router.get("/fraud", response_model=FraudStatisticsResponse)
def get_fraud(
    db: DatabaseSession,
    current_user: User = Depends(get_current_user),
) -> FraudStatisticsResponse:
    return get_fraud_statistics(db, current_user)
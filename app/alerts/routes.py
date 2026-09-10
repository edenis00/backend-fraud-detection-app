from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.alerts.schemas import (
    FraudAlertListResponse,
    FraudAlertResponse,
    FraudAlertUpdate,
)
from app.alerts.service import (
    calculate_total_pages,
    get_alert_by_id,
    list_alerts,
    update_alert,
)
from app.auth.dependencies import get_current_user
from app.core.enums import AlertStatus
from app.database.session import get_db
from app.users.models import User

router = APIRouter(prefix="/api/alerts", tags=["fraud alerts"])

DatabaseSession = Annotated[Session, Depends(get_db)]


@router.get("", response_model=FraudAlertListResponse)
def get_alerts(
    db: DatabaseSession,
    current_user: User = Depends(get_current_user),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    alert_status: AlertStatus | None = None,
    rule_name: str | None = None,
    transaction_reference: str | None = None,
) -> FraudAlertListResponse:
    items, total = list_alerts(
        db,
        current_user,
        page=page,
        page_size=page_size,
        alert_status=alert_status,
        rule_name=rule_name,
        transaction_reference=transaction_reference,
    )

    return FraudAlertListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=calculate_total_pages(total, page_size),
    )


@router.get("/{alert_id}", response_model=FraudAlertResponse)
def get_alert(
    alert_id: int,
    db: DatabaseSession,
    current_user: User = Depends(get_current_user),
) -> FraudAlertResponse:
    alert = get_alert_by_id(db, current_user, alert_id)

    if alert is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Fraud alert not found.",
        )

    return alert


@router.put("/{alert_id}", response_model=FraudAlertResponse)
def update_alert_status(
    alert_id: int,
    payload: FraudAlertUpdate,
    db: DatabaseSession,
    current_user: User = Depends(get_current_user),
) -> FraudAlertResponse:
    alert = get_alert_by_id(db, current_user, alert_id)

    if alert is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Fraud alert not found.",
        )

    return update_alert(db, alert, payload)
from datetime import datetime, timezone
from math import ceil

from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from app.alerts.models import FraudAlert
from app.alerts.schemas import FraudAlertUpdate
from app.core.enums import AlertStatus
from app.transactions.models import Transaction
from app.users.models import User


def list_alerts(
    db: Session,
    user: User,
    *,
    page: int,
    page_size: int,
    alert_status: AlertStatus | None = None,
    rule_name: str | None = None,
    transaction_reference: str | None = None,
) -> tuple[list[FraudAlert], int]:
    filters = [Transaction.user_id == user.id]

    if alert_status:
        filters.append(FraudAlert.alert_status == alert_status)
    if rule_name:
        filters.append(FraudAlert.rule_name.ilike(f"%{rule_name}%"))
    if transaction_reference:
        filters.append(
            Transaction.transaction_reference.ilike(f"%{transaction_reference}%")
        )

    total = db.scalar(
        select(func.count(FraudAlert.id))
        .join(FraudAlert.transaction)
        .where(*filters)
    ) or 0

    alerts = db.scalars(
        select(FraudAlert)
        .join(FraudAlert.transaction)
        .options(joinedload(FraudAlert.transaction))
        .where(*filters)
        .order_by(FraudAlert.created_at.desc(), FraudAlert.id.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).all()

    return list(alerts), total


def get_alert_by_id(
    db: Session,
    user: User,
    alert_id: int,
) -> FraudAlert | None:
    return db.scalar(
        select(FraudAlert)
        .join(FraudAlert.transaction)
        .options(joinedload(FraudAlert.transaction))
        .where(
            FraudAlert.id == alert_id,
            Transaction.user_id == user.id,
        )
    )


def update_alert(
    db: Session,
    alert: FraudAlert,
    payload: FraudAlertUpdate,
) -> FraudAlert:
    alert.alert_status = payload.alert_status

    if (
        payload.alert_status in {AlertStatus.REVIEWED, AlertStatus.RESOLVED}
        and alert.reviewed_at is None
    ):
        alert.reviewed_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(alert)

    return alert


def calculate_total_pages(total: int, page_size: int) -> int:
    return ceil(total / page_size) if total else 0
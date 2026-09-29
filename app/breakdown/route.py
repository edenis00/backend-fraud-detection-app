from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.alerts.models import FraudAlert
from app.auth.dependencies import get_current_user
from app.cards.models import Card
from app.core.config import get_settings
from app.core.enums import FraudStatus
from app.database.session import get_db
from app.departments.models import Department
from app.fraud_rules.models import FraudRule
from app.transactions.models import Transaction
from app.users.models import User

settings = get_settings()
router = APIRouter(prefix=f"{settings.api_prefix}/analysis", tags=["analysis"])

DatabaseSession = Annotated[Session, Depends(get_db)]


def _bucket_rows(db: Session, label_column, filters: list, *, joins=(), limit: int) -> list[dict]:
    statement = (
        select(
            label_column.label("label"),
            func.count(Transaction.id).label("count"),
            func.coalesce(func.sum(Transaction.amount), 0).label("value"),
            func.count(Transaction.id)
            .filter(Transaction.fraud_status == FraudStatus.SUSPICIOUS)
            .label("suspicious"),
        )
        .select_from(Transaction)
    )

    for join_target, condition in joins:
        statement = statement.outerjoin(join_target, condition)

    rows = db.execute(
        statement.where(*filters)
        .group_by(label_column)
        .order_by(func.sum(Transaction.amount).desc(), label_column)
        .limit(limit)
    ).all()

    return [
        {
            "label": row.label,
            "count": row.count,
            "value": row.value,
            "suspicious": row.suspicious,
        }
        for row in rows
    ]


@router.get("/breakdown")
def get_breakdown(
    db: DatabaseSession,
    current_user: User = Depends(get_current_user),
    transaction_type: str | None = Query(default=None, alias="type"),
    limit: int = Query(default=10, ge=1, le=100),
) -> dict:
    """Return transaction and alert groupings for the dashboard and analysis pages."""
    filters = [Transaction.user_id == current_user.id]
    if transaction_type:
        filters.append(Transaction.transaction_type == transaction_type)

    unassigned = "Unassigned"
    by_department = _bucket_rows(
        db,
        func.coalesce(Department.name, unassigned),
        filters,
        joins=((Department, Transaction.department_id == Department.id),),
        limit=limit,
    )
    by_user = _bucket_rows(
        db,
        User.full_name,
        filters,
        joins=((User, Transaction.user_id == User.id),),
        limit=limit,
    )
    by_card = _bucket_rows(
        db,
        func.coalesce(Card.card_reference, Transaction.card_reference),
        filters,
        joins=((Card, Transaction.card_id == Card.id),),
        limit=limit,
    )
    by_type = _bucket_rows(db, Transaction.transaction_type, filters, limit=limit)
    by_location = _bucket_rows(db, Transaction.location, filters, limit=limit)

    rule_severities = dict(
        db.execute(select(FraudRule.rule_name, FraudRule.severity)).all()
    )
    rule_rows = db.execute(
        select(FraudAlert.rule_name, func.count(FraudAlert.id).label("count"))
        .join(FraudAlert.transaction)
        .where(*filters)
        .group_by(FraudAlert.rule_name)
        .order_by(func.count(FraudAlert.id).desc(), FraudAlert.rule_name)
        .limit(limit)
    ).all()
    status_rows = db.execute(
        select(FraudAlert.alert_status, func.count(FraudAlert.id).label("count"))
        .join(FraudAlert.transaction)
        .where(*filters)
        .group_by(FraudAlert.alert_status)
        .order_by(FraudAlert.alert_status)
    ).all()

    total_transactions = db.scalar(
        select(func.count(Transaction.id)).where(*filters)
    ) or 0
    suspicious_transactions = db.scalar(
        select(func.count(Transaction.id)).where(
            *filters,
            Transaction.fraud_status == FraudStatus.SUSPICIOUS,
        )
    ) or 0

    return {
        "by_department": by_department,
        "by_user": by_user,
        "by_card": by_card,
        "by_type": by_type,
        "by_location": by_location,
        "by_rule": [
            {
                "rule_name": row.rule_name,
                "severity": str(rule_severities.get(row.rule_name, "High")).title(),
                "count": row.count,
            }
            for row in rule_rows
        ],
        "by_alert_status": [
            {
                "alert_status": str(row.alert_status.value).replace("_", " ").title(),
                "count": row.count,
            }
            for row in status_rows
        ],
        "suspicious_rate": suspicious_transactions / total_transactions
        if total_transactions
        else 0,
    }

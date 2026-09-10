from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Date, cast, func, select
from sqlalchemy.orm import Session

from app.alerts.models import FraudAlert
from app.core.enums import FraudStatus
from app.transactions.models import Transaction
from app.users.models import User


def get_dashboard_summary(db: Session, user: User) -> dict:
    transaction_counts = db.execute(
        select(
            func.count(Transaction.id).label("total_transactions"),
            func.count(Transaction.id)
            .filter(Transaction.fraud_status == FraudStatus.NORMAL)
            .label("normal_transactions"),
            func.count(Transaction.id)
            .filter(Transaction.fraud_status == FraudStatus.SUSPICIOUS)
            .label("suspicious_transactions"),
            func.coalesce(func.sum(Transaction.amount), 0).label(
                "total_transaction_value"
            ),
        ).where(Transaction.user_id == user.id)
    ).one()

    fraud_alert_count = db.scalar(
        select(func.count(FraudAlert.id))
        .join(FraudAlert.transaction)
        .where(Transaction.user_id == user.id)
    ) or 0

    return {
        "total_transactions": transaction_counts.total_transactions or 0,
        "normal_transactions": transaction_counts.normal_transactions or 0,
        "suspicious_transactions": transaction_counts.suspicious_transactions or 0,
        "fraud_alert_count": fraud_alert_count,
        "total_transaction_value": (
            transaction_counts.total_transaction_value or Decimal("0")
        ),
    }


def get_transaction_trends(
    db: Session,
    user: User,
    start_date: datetime | None = None,
    end_date: datetime | None = None,
) -> list[dict]:
    filters = [Transaction.user_id == user.id]

    if start_date:
        filters.append(Transaction.transaction_date >= start_date)
    if end_date:
        filters.append(Transaction.transaction_date <= end_date)

    day = cast(Transaction.transaction_date, Date).label("date")
    rows = db.execute(
        select(
            day,
            func.count(Transaction.id).label("transaction_count"),
            func.coalesce(func.sum(Transaction.amount), 0).label("total_value"),
            func.count(Transaction.id)
            .filter(Transaction.fraud_status == FraudStatus.SUSPICIOUS)
            .label("suspicious_count"),
        )
        .where(*filters)
        .group_by(day)
        .order_by(day)
    ).all()

    return [
        {
            "date": row.date,
            "transaction_count": row.transaction_count,
            "total_value": row.total_value,
            "suspicious_count": row.suspicious_count,
        }
        for row in rows
    ]


def get_distribution(
    db: Session,
    user: User,
    field_name: str,
) -> list[dict]:
    category_column = (
        Transaction.transaction_type
        if field_name == "transaction_type"
        else Transaction.location
    )

    rows = db.execute(
        select(
            category_column.label("category"),
            func.count(Transaction.id).label("transaction_count"),
            func.coalesce(func.sum(Transaction.amount), 0).label("total_value"),
            func.count(Transaction.id)
            .filter(Transaction.fraud_status == FraudStatus.SUSPICIOUS)
            .label("suspicious_count"),
        )
        .where(Transaction.user_id == user.id)
        .group_by(category_column)
        .order_by(func.count(Transaction.id).desc())
    ).all()

    return [
        {
            "category": row.category,
            "transaction_count": row.transaction_count,
            "total_value": row.total_value,
            "suspicious_count": row.suspicious_count,
        }
        for row in rows
    ]


def get_fraud_statistics(db: Session, user: User) -> dict:
    normal_transactions = db.scalar(
        select(func.count(Transaction.id)).where(
            Transaction.user_id == user.id,
            Transaction.fraud_status == FraudStatus.NORMAL,
        )
    ) or 0

    suspicious_transactions = db.scalar(
        select(func.count(Transaction.id)).where(
            Transaction.user_id == user.id,
            Transaction.fraud_status == FraudStatus.SUSPICIOUS,
        )
    ) or 0

    alerts_by_status_rows = db.execute(
        select(
            FraudAlert.alert_status,
            func.count(FraudAlert.id).label("count"),
        )
        .join(FraudAlert.transaction)
        .where(Transaction.user_id == user.id)
        .group_by(FraudAlert.alert_status)
        .order_by(FraudAlert.alert_status)
    ).all()

    alerts_by_rule_rows = db.execute(
        select(
            FraudAlert.rule_name,
            func.count(FraudAlert.id).label("count"),
        )
        .join(FraudAlert.transaction)
        .where(Transaction.user_id == user.id)
        .group_by(FraudAlert.rule_name)
        .order_by(func.count(FraudAlert.id).desc())
    ).all()

    return {
        "normal_transactions": normal_transactions,
        "suspicious_transactions": suspicious_transactions,
        "total_alerts": sum(row.count for row in list(alerts_by_status_rows)),
        "alerts_by_status": [
            {"alert_status": row.alert_status, "count": row.count}
            for row in alerts_by_status_rows
        ],
        "alerts_by_rule": [
            {"rule_name": row.rule_name, "count": row.count}
            for row in alerts_by_rule_rows
        ],
    }
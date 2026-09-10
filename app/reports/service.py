from datetime import datetime, timezone
from math import ceil

from fastapi.encoders import jsonable_encoder
from sqlalchemy import Date, cast, func, select
from sqlalchemy.orm import Session

from app.alerts.models import FraudAlert
from app.core.enums import FraudStatus
from app.reports.models import Report
from app.reports.schemas import ReportGenerateRequest
from app.transactions.models import Transaction
from app.users.models import User


def _ensure_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)

    return value


def _transaction_filters(
    user: User,
    start_date: datetime,
    end_date: datetime,
) -> list:
    return [
        Transaction.user_id == user.id,
        Transaction.transaction_date >= start_date,
        Transaction.transaction_date <= end_date,
    ]


def _build_report_data(
    db: Session,
    user: User,
    start_date: datetime,
    end_date: datetime,
) -> dict:
    filters = _transaction_filters(user, start_date, end_date)

    summary_row = db.execute(
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
        ).where(*filters)
    ).one()

    alert_count = db.scalar(
        select(func.count(FraudAlert.id))
        .join(FraudAlert.transaction)
        .where(*filters)
    ) or 0

    day = cast(Transaction.transaction_date, Date).label("date")
    trend_rows = db.execute(
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

    def build_distribution(column) -> list[dict]:
        rows = db.execute(
            select(
                column.label("category"),
                func.count(Transaction.id).label("transaction_count"),
                func.coalesce(func.sum(Transaction.amount), 0).label("total_value"),
                func.count(Transaction.id)
                .filter(Transaction.fraud_status == FraudStatus.SUSPICIOUS)
                .label("suspicious_count"),
            )
            .where(*filters)
            .group_by(column)
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

    rule_rows = db.execute(
        select(
            FraudAlert.rule_name,
            func.count(FraudAlert.id).label("count"),
        )
        .join(FraudAlert.transaction)
        .where(*filters)
        .group_by(FraudAlert.rule_name)
        .order_by(func.count(FraudAlert.id).desc())
    ).all()

    report_data = {
        "period": {
            "start_date": start_date,
            "end_date": end_date,
        },
        "summary": {
            "total_transactions": summary_row.total_transactions or 0,
            "normal_transactions": summary_row.normal_transactions or 0,
            "suspicious_transactions": summary_row.suspicious_transactions or 0,
            "fraud_alert_count": alert_count,
            "total_transaction_value": (
                summary_row.total_transaction_value or 0
            ),
        },
        "daily_trends": [
            {
                "date": row.date,
                "transaction_count": row.transaction_count,
                "total_value": row.total_value,
                "suspicious_count": row.suspicious_count,
            }
            for row in trend_rows
        ],
        "distribution_by_type": build_distribution(Transaction.transaction_type),
        "distribution_by_location": build_distribution(Transaction.location),
        "alerts_by_rule": [
            {
                "rule_name": row.rule_name,
                "count": row.count,
            }
            for row in rule_rows
        ],
    }

    return jsonable_encoder(report_data)


def generate_report(
    db: Session,
    user: User,
    payload: ReportGenerateRequest,
) -> Report:
    start_date = _ensure_utc(payload.start_date)
    end_date = _ensure_utc(payload.end_date)

    report = Report(
        report_type=payload.report_type,
        start_date=start_date,
        end_date=end_date,
        generated_by=user.id,
        report_data=_build_report_data(db, user, start_date, end_date),
    )
    db.add(report)
    db.commit()
    db.refresh(report)

    return report


def list_reports(
    db: Session,
    user: User,
    page: int,
    page_size: int,
) -> tuple[list[Report], int]:
    total = db.scalar(
        select(func.count(Report.id)).where(Report.generated_by == user.id)
    ) or 0

    reports = db.scalars(
        select(Report)
        .where(Report.generated_by == user.id)
        .order_by(Report.created_at.desc(), Report.id.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).all()

    return list(reports), total


def get_report_by_id(
    db: Session,
    user: User,
    report_id: int,
) -> Report | None:
    return db.scalar(
        select(Report).where(
            Report.id == report_id,
            Report.generated_by == user.id,
        )
    )


def calculate_total_pages(total: int, page_size: int) -> int:
    return ceil(total / page_size) if total else 0
from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal
from math import ceil

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.alerts.models import FraudAlert
from app.core.enums import FraudStatus, TransactionStatus
from app.fraud_detection.service import evaluate_transaction
from app.transactions.models import Transaction
from app.transactions.schemas import TransactionCreate
from app.users.models import User


@dataclass
class ProcessedTransaction:
    transaction: Transaction
    alert_ids: list[int]
    triggered_rules: list[str]


def process_transaction(
    db: Session,
    user: User,
    payload: TransactionCreate,
) -> ProcessedTransaction:
    existing = db.scalar(
        select(Transaction).where(
            Transaction.transaction_reference == payload.transaction_reference
        )
    )
    if existing:
        raise ValueError("Transaction reference already exists.")

    transaction_date = payload.transaction_date
    if transaction_date.tzinfo is None:
        transaction_date = transaction_date.replace(tzinfo=timezone.utc)

    transaction = Transaction(
        transaction_reference=payload.transaction_reference,
        user_id=user.id,
        card_reference=payload.card_reference,
        amount=payload.amount,
        transaction_type=payload.transaction_type,
        location=payload.location,
        transaction_date=transaction_date,
    )
    db.add(transaction)
    db.flush()

    rule_matches = evaluate_transaction(db, transaction)

    if rule_matches:
        transaction.fraud_status = FraudStatus.SUSPICIOUS

        alerts = [
            FraudAlert(
                transaction_id=transaction.id,
                rule_name=match.rule_name,
                reason=match.reason,
            )
            for match in rule_matches
        ]
        db.add_all(alerts)
        db.flush()
        alert_ids = [alert.id for alert in alerts]
    else:
        alert_ids = []

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise ValueError("Transaction reference already exists.")

    db.refresh(transaction)

    return ProcessedTransaction(
        transaction=transaction,
        alert_ids=alert_ids,
        triggered_rules=[match.rule_name for match in rule_matches],
    )


def list_transactions(
    db: Session,
    user: User,
    *,
    page: int,
    page_size: int,
    transaction_reference: str | None = None,
    transaction_type: str | None = None,
    location: str | None = None,
    status: TransactionStatus | None = None,
    fraud_status: FraudStatus | None = None,
    min_amount: Decimal | None = None,
    max_amount: Decimal | None = None,
    start_date: datetime | None = None,
    end_date: datetime | None = None,
) -> tuple[list[Transaction], int]:
    filters = [Transaction.user_id == user.id]

    if transaction_reference:
        filters.append(
            Transaction.transaction_reference.ilike(f"%{transaction_reference}%")
        )
    if transaction_type:
        filters.append(Transaction.transaction_type.ilike(f"%{transaction_type}%"))
    if location:
        filters.append(Transaction.location.ilike(f"%{location}%"))
    if status:
        filters.append(Transaction.status == status)
    if fraud_status:
        filters.append(Transaction.fraud_status == fraud_status)
    if min_amount is not None:
        filters.append(Transaction.amount >= min_amount)
    if max_amount is not None:
        filters.append(Transaction.amount <= max_amount)
    if start_date:
        filters.append(Transaction.transaction_date >= start_date)
    if end_date:
        filters.append(Transaction.transaction_date <= end_date)

    total = db.scalar(
        select(func.count(Transaction.id)).where(*filters)
    ) or 0

    transactions = db.scalars(
        select(Transaction)
        .where(*filters)
        .order_by(Transaction.transaction_date.desc(), Transaction.id.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).all()

    return list(transactions), total


def get_transaction_by_id(
    db: Session,
    user: User,
    transaction_id: int,
) -> Transaction | None:
    return db.scalar(
        select(Transaction).where(
            Transaction.id == transaction_id,
            Transaction.user_id == user.id,
        )
    )


def calculate_total_pages(total: int, page_size: int) -> int:
    return ceil(total / page_size) if total else 0
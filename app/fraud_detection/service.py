from collections import Counter
from datetime import timedelta
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.fraud_detection.rules import (
    HIGH_FREQUENCY_RULE,
    UNUSUAL_LOCATION_RULE,
    FraudRuleMatch,
    check_high_amount,
)
from app.transactions.models import Transaction


def evaluate_transaction(
    db: Session,
    transaction: Transaction,
) -> list[FraudRuleMatch]:
    settings = get_settings()
    matches: list[FraudRuleMatch] = []

    high_amount_match = check_high_amount(
        transaction.amount,
        Decimal(str(settings.fraud_amount_threshold)),
    )
    if high_amount_match:
        matches.append(high_amount_match)

    window_start = transaction.transaction_date - timedelta(
        minutes=settings.fraud_frequency_window_minutes
    )
    frequency_count = db.scalar(
        select(func.count(Transaction.id)).where(
            Transaction.user_id == transaction.user_id,
            Transaction.card_reference == transaction.card_reference,
            Transaction.transaction_date >= window_start,
            Transaction.transaction_date <= transaction.transaction_date,
        )
    )

    if frequency_count and frequency_count >= settings.fraud_frequency_limit:
        matches.append(
            FraudRuleMatch(
                rule_name=HIGH_FREQUENCY_RULE,
                reason=(
                    f"{frequency_count} transactions using this card reference "
                    f"occurred within {settings.fraud_frequency_window_minutes} minutes."
                ),
            )
        )

    location_history = db.scalars(
        select(Transaction.location)
        .where(
            Transaction.user_id == transaction.user_id,
            Transaction.card_reference == transaction.card_reference,
            Transaction.transaction_date < transaction.transaction_date,
        )
        .order_by(Transaction.transaction_date.desc())
        .limit(50)
    ).all()

    if len(location_history) >= settings.fraud_location_history_minimum:
        normalized_locations = [
            location.strip().casefold() for location in location_history
        ]
        location_counts = Counter(normalized_locations)
        established_location, established_count = location_counts.most_common(1)[0]
        dominance_ratio = established_count / len(normalized_locations)
        current_location = transaction.location.strip().casefold()

        if (
            current_location != established_location
            and dominance_ratio >= settings.fraud_location_dominance_ratio
        ):
            matches.append(
                FraudRuleMatch(
                    rule_name=UNUSUAL_LOCATION_RULE,
                    reason=(
                        f"Transaction location '{transaction.location}' differs from "
                        f"the established location pattern for this card reference."
                    ),
                )
            )

    return matches
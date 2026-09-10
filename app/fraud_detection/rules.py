from dataclasses import dataclass
from decimal import Decimal


HIGH_AMOUNT_RULE = "High Transaction Amount"
HIGH_FREQUENCY_RULE = "High Transaction Frequency"
UNUSUAL_LOCATION_RULE = "Unusual Location"


@dataclass(frozen=True)
class FraudRuleMatch:
    rule_name: str
    reason: str


def check_high_amount(
    amount: Decimal,
    threshold: Decimal,
) -> FraudRuleMatch | None:
    if amount > threshold:
        return FraudRuleMatch(
            rule_name=HIGH_AMOUNT_RULE,
            reason=(
                f"Transaction amount {amount} exceeds the configured "
                f"threshold of {threshold}."
            ),
        )

    return None
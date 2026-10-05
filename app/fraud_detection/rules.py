from dataclasses import dataclass
from decimal import Decimal
from statistics import median


HIGH_AMOUNT_RULE = "High Transaction Amount"
HIGH_FREQUENCY_RULE = "High Transaction Frequency"
UNUSUAL_LOCATION_RULE = "Unusual Location"
UNUSUAL_SPENDING_RULE = "Unusual Spending Pattern"
MIN_SPENDING_HISTORY = 5
SPENDING_PATTERN_MULTIPLIER = Decimal("3")



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


def check_spending_pattern(
    amount: Decimal,
    historical_amounts: list[Decimal],
) -> FraudRuleMatch | None:
    if len(historical_amounts) < MIN_SPENDING_HISTORY:
        return None

    baseline = Decimal(str(median(historical_amounts)))
    deviations = [abs(value - baseline) for value in historical_amounts]
    median_deviation = Decimal(str(median(deviations)))

    if median_deviation == 0:
        is_unusual = amount >= baseline * SPENDING_PATTERN_MULTIPLIER
    else:
        is_unusual = amount > baseline + (
            SPENDING_PATTERN_MULTIPLIER * median_deviation
        )

    if not is_unusual:
        return None

    return FraudRuleMatch(
        rule_name=UNUSUAL_SPENDING_RULE,
        reason=(
            f"Transaction amount {amount} is unusually high for this card. "
            f"The recent median amount is {baseline}."
        ),
    )
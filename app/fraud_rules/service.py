from sqlalchemy.orm import Session
from app.fraud_rules.models import FraudRule
from app.fraud_rules.schemas import FraudRuleCreate, FraudRuleUpdate


class FraudRuleService:
    """Service layer for fraud rule operations."""

    @staticmethod
    def create_rule(db: Session, rule: FraudRuleCreate) -> FraudRule:
        """Create a new fraud rule."""
        db_rule = FraudRule(
            rule_code=rule.rule_code,
            rule_name=rule.rule_name,
            description=rule.description,
            threshold=rule.threshold,
            severity=rule.severity,
            status=rule.status,
        )
        db.add(db_rule)
        db.commit()
        db.refresh(db_rule)
        return db_rule

    @staticmethod
    def get_rule(db: Session, rule_id: int) -> FraudRule | None:
        """Get fraud rule by ID."""
        return db.query(FraudRule).filter(FraudRule.id == rule_id).first()

    @staticmethod
    def get_rule_by_code(db: Session, code: str) -> FraudRule | None:
        """Get fraud rule by code."""
        return db.query(FraudRule).filter(FraudRule.rule_code == code).first()

    @staticmethod
    def list_rules(db: Session, skip: int = 0, limit: int = 100) -> list[FraudRule]:
        """List all fraud rules."""
        return db.query(FraudRule).offset(skip).limit(limit).all()

    @staticmethod
    def get_active_rules(db: Session) -> list[FraudRule]:
        """Get all active fraud rules."""
        return db.query(FraudRule).filter(FraudRule.status == "active").all()

    @staticmethod
    def update_rule(db: Session, rule_id: int, rule_update: FraudRuleUpdate) -> FraudRule | None:
        """Update a fraud rule."""
        db_rule = db.query(FraudRule).filter(FraudRule.id == rule_id).first()
        if not db_rule:
            return None
        
        update_data = rule_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_rule, key, value)
        
        db.commit()
        db.refresh(db_rule)
        return db_rule

    @staticmethod
    def delete_rule(db: Session, rule_id: int) -> bool:
        """Delete a fraud rule."""
        db_rule = db.query(FraudRule).filter(FraudRule.id == rule_id).first()
        if not db_rule:
            return False
        
        db.delete(db_rule)
        db.commit()
        return True

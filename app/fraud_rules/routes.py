from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.database.session import get_db
from app.auth.dependencies import get_current_user
from app.users.models import User
from app.fraud_rules.service import FraudRuleService
from app.fraud_rules.schemas import FraudRuleCreate, FraudRuleUpdate, FraudRuleResponse

settings = get_settings()
router = APIRouter(prefix=f"{settings.api_prefix}/fraud-rules", tags=["fraud-rules"])


@router.post("", response_model=FraudRuleResponse, status_code=status.HTTP_201_CREATED)
def create_fraud_rule(
    rule: FraudRuleCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a new fraud rule (admin/fraud_analyst only)."""
    if current_user.role not in ["admin", "fraud_analyst"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins and fraud analysts can create rules",
        )
    
    existing = FraudRuleService.get_rule_by_code(db, rule.rule_code)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Rule code already exists",
        )
    
    return FraudRuleService.create_rule(db, rule)


@router.get("/{rule_id}", response_model=FraudRuleResponse)
def get_fraud_rule(
    rule_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get a fraud rule by ID."""
    rule = FraudRuleService.get_rule(db, rule_id)
    if not rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Fraud rule not found",
        )
    return rule


@router.get("", response_model=list[FraudRuleResponse])
def list_fraud_rules(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List all fraud rules."""
    return FraudRuleService.list_rules(db, skip=skip, limit=limit)


@router.get("/active/all", response_model=list[FraudRuleResponse])
def get_active_fraud_rules(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get all active fraud rules."""
    return FraudRuleService.get_active_rules(db)


@router.put("/{rule_id}", response_model=FraudRuleResponse)
def update_fraud_rule(
    rule_id: int,
    rule_update: FraudRuleUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update a fraud rule (admin/fraud_analyst only)."""
    if current_user.role not in ["admin", "fraud_analyst"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins and fraud analysts can update rules",
        )
    
    rule = FraudRuleService.update_rule(db, rule_id, rule_update)
    if not rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Fraud rule not found",
        )
    return rule


@router.delete("/{rule_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_fraud_rule(
    rule_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete a fraud rule (admin only)."""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can delete rules",
        )
    
    success = FraudRuleService.delete_rule(db, rule_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Fraud rule not found",
        )

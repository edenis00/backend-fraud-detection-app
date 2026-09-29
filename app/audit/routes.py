from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.database.session import get_db
from app.auth.dependencies import get_current_user
from app.users.models import User
from app.audit.service import AuditLogService
from app.audit.schemas import AuditLogResponse

settings = get_settings()
router = APIRouter(prefix=f"{settings.api_prefix}/audit-logs", tags=["audit-logs"])


@router.get("/{log_id}", response_model=AuditLogResponse)
def get_audit_log(
    log_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get an audit log by ID (admin/fraud_analyst only)."""
    if current_user.role not in ["admin", "fraud_analyst"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins and fraud analysts can view audit logs",
        )
    
    log = AuditLogService.get_audit_log(db, log_id)
    if not log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Audit log not found",
        )
    return log


@router.get("/user/{user_id}", response_model=list[AuditLogResponse])
def get_user_audit_logs(
    user_id: int,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get audit logs for a specific user (admin/fraud_analyst only)."""
    if current_user.role not in ["admin", "fraud_analyst"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins and fraud analysts can view audit logs",
        )
    
    return AuditLogService.get_user_audit_logs(db, user_id, skip=skip, limit=limit)


@router.get("/entity/{entity_type}/{entity_id}", response_model=list[AuditLogResponse])
def get_entity_audit_logs(
    entity_type: str,
    entity_id: int,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get audit logs for a specific entity (admin/fraud_analyst only)."""
    if current_user.role not in ["admin", "fraud_analyst"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins and fraud analysts can view audit logs",
        )
    
    return AuditLogService.get_entity_audit_logs(
        db, entity_type, entity_id, skip=skip, limit=limit
    )


@router.get("", response_model=list[AuditLogResponse])
def list_audit_logs(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List all audit logs (admin/fraud_analyst only)."""
    if current_user.role not in ["admin", "fraud_analyst"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins and fraud analysts can view audit logs",
        )
    
    return AuditLogService.list_audit_logs(db, skip=skip, limit=limit)

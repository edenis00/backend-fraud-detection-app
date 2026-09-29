from sqlalchemy.orm import Session
from app.audit.models import AuditLog
from app.audit.schemas import AuditLogCreate


class AuditLogService:
    """Service layer for audit log operations."""

    @staticmethod
    def log_action(db: Session, log: AuditLogCreate) -> AuditLog:
        """Log an audit action."""
        db_log = AuditLog(
            user_id=log.user_id,
            action=log.action,
            entity_type=log.entity_type,
            entity_id=log.entity_id,
            details=log.details,
        )
        db.add(db_log)
        db.commit()
        db.refresh(db_log)
        return db_log

    @staticmethod
    def get_audit_log(db: Session, log_id: int) -> AuditLog | None:
        """Get audit log by ID."""
        return db.query(AuditLog).filter(AuditLog.id == log_id).first()

    @staticmethod
    def get_user_audit_logs(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> list[AuditLog]:
        """Get audit logs for a specific user."""
        return (
            db.query(AuditLog)
            .filter(AuditLog.user_id == user_id)
            .order_by(AuditLog.timestamp.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    @staticmethod
    def get_entity_audit_logs(
        db: Session, entity_type: str, entity_id: int, skip: int = 0, limit: int = 100
    ) -> list[AuditLog]:
        """Get audit logs for a specific entity."""
        return (
            db.query(AuditLog)
            .filter(AuditLog.entity_type == entity_type, AuditLog.entity_id == entity_id)
            .order_by(AuditLog.timestamp.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    @staticmethod
    def list_audit_logs(db: Session, skip: int = 0, limit: int = 100) -> list[AuditLog]:
        """List all audit logs."""
        return (
            db.query(AuditLog)
            .order_by(AuditLog.timestamp.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

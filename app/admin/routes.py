from fastapi import APIRouter, Depends, HTTPException, status

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.core.enums import UserRole
from app.core.security import hash_password
from app.database.session import get_db
from app.users.models import User
from app.users.schemas import UserResponse
from app.departments.models import Department
from app.admin.schemas import AdminUserCreate, AdminRoleUpdate, AmountThresholdUpdate, AmountThresholdResponse
from app.fraud_rules.models import FraudRule

router = APIRouter(prefix="/api/admin", tags=["admin"])



def require_admin(
    current_user: User = Depends(get_current_user),
) -> User:
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    return current_user

@router.put(
    "/settings/fraud-threshold",
    response_model=AmountThresholdResponse,
)
def update_amount_threshold(
    payload: AmountThresholdUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
) -> AmountThresholdResponse:
    rule = db.scalar(
        select(FraudRule).where(FraudRule.rule_code == "HIGH_AMOUNT")
    )

    if rule is None:
        rule = FraudRule(
            rule_code="HIGH_AMOUNT",
            rule_name="High Transaction Amount",
            description="Flags transactions above the administrator-set amount limit.",
            threshold=payload.threshold,
            severity="high",
            status="active",
        )
        db.add(rule)
    else:
        rule.threshold = payload.threshold
        rule.status = "active"

    db.commit()
    db.refresh(rule)
    return AmountThresholdResponse(threshold=rule.threshold)

@router.get("/users", response_model=list[UserResponse])
def list_users(
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
) -> list[User]:
    return list(db.scalars(select(User).order_by(User.id)).all())


@router.post(
    "/users",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_user(
    payload: AdminUserCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
) -> User:
    email = str(payload.email).lower()

    existing = db.scalar(select(User).where(User.email == email))
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists.",
        )

    if payload.department_id is not None and db.get(Department, payload.department_id) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Department not found",
    )

    user = User(
        full_name=payload.full_name,
        email=email,
        password_hash=hash_password(payload.password),
        role=payload.role,
        department_id=payload.department_id,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.patch("/users/{user_id}/role", response_model=UserResponse)
def update_user_role(
    user_id: int,
    payload: AdminRoleUpdate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(require_admin),
) -> User:
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # Prevent an admin from accidentally removing their own admin access.
    if user.id == current_admin.id and payload.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot remove your own admin role.",
        )

    if user.role == UserRole.ADMIN and payload.role != UserRole.ADMIN:
        admin_count = db.scalar(
            select(func.count())
            .select_from(User)
            .where(User.role == UserRole.ADMIN)
        )
        if admin_count <= 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="The last admin account cannot be demoted.",
            )

    user.role = payload.role
    db.commit()
    db.refresh(user)
    return user
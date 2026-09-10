from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth.schemas import RegistrationRequest
from app.core.enums import UserRole
from app.core.security import hash_password, verify_password
from app.users.models import User


def get_user_by_email(db: Session, email: str) -> User | None:
    statement = select(User).where(User.email == email.lower())
    return db.scalar(statement)


def register_user(db: Session, payload: RegistrationRequest) -> User:
    email = payload.email.lower()

    if get_user_by_email(db, email):
        raise ValueError("An account with this email already exists.")

    user = User(
        full_name=payload.full_name,
        email=email,
        password_hash=hash_password(payload.password),
        role=UserRole.ANALYST,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    return user


def authenticate_user(
    db: Session,
    email: str,
    password: str,
) -> User | None:
    user = get_user_by_email(db, email)

    if user is None or not verify_password(password, user.password_hash):
        return None

    return user
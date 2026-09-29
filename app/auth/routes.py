import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.auth.schemas import LoginRequest, RegistrationRequest, TokenResponse
from app.auth.service import authenticate_user, register_user
from app.core.config import get_settings
from app.core.security import create_access_token
from app.database.session import get_db
from app.users.models import User
from app.users.schemas import UserResponse

logger = logging.getLogger("app.auth")

settings = get_settings()
router = APIRouter(prefix=f"{settings.api_prefix}/auth", tags=["authentication"])

DatabaseSession = Annotated[Session, Depends(get_db)]


def _mask_email(email: str) -> str:
    if "@" not in email:
        return "***"
    local, domain = email.split("@", 1)
    masked_local = local[:2] + "***" if len(local) > 2 else "*"
    return f"{masked_local}@{domain}"


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def register(payload: RegistrationRequest, db: DatabaseSession) -> User:
    email = str(payload.email)
    logger.info("Registration attempt for %s", _mask_email(email))
    try:
        user = register_user(db, payload)
        logger.info("User registered successfully: user_id=%s email=%s", user.id, _mask_email(email))
        return user
    except ValueError as error:
        logger.warning("Registration failed for %s: %s", _mask_email(email), error)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        )
    except Exception as error:  # unexpected errors (DB, etc.)
        logger.exception("Unexpected registration error for %s", _mask_email(email))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An internal error occurred during registration.",
        )


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: DatabaseSession) -> TokenResponse:
    email = str(payload.email)
    logger.info("Login attempt for %s", _mask_email(email))
    try:
        user = authenticate_user(db, email, payload.password)
    except Exception:
        logger.exception("Authentication error for %s", _mask_email(email))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An internal error occurred during authentication.",
        )

    if user is None:
        logger.warning("Failed login for %s", _mask_email(email))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        settings = get_settings()
        token = create_access_token(user.id, user.role.value)
        logger.info("Successful login for user_id=%s email=%s", user.id, _mask_email(email))

        return TokenResponse(
            access_token=token,
            expires_in=settings.access_token_expire_minutes * 60,
        )
    except Exception:
        logger.exception("Token creation/error response for %s", _mask_email(email))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An internal error occurred while creating session.",
        )


@router.post("/logout")
def logout(current_user: User = Depends(get_current_user)) -> dict[str, str]:
    logger.info("User logged out: user_id=%s email=%s", current_user.id, _mask_email(str(current_user.email)))
    return {"status": "ok"}


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)) -> User:
    return current_user
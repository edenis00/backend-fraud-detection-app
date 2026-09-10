from datetime import datetime
from decimal import Decimal
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.core.enums import FraudStatus, TransactionStatus
from app.database.session import get_db
from app.transactions.schemas import (
    TransactionCreate,
    TransactionListResponse,
    TransactionProcessResponse,
    TransactionResponse,
)
from app.transactions.service import (
    calculate_total_pages,
    get_transaction_by_id,
    list_transactions,
    process_transaction,
)
from app.users.models import User
from app.transactions.models import Transaction

router = APIRouter(prefix="/api/transactions", tags=["transactions"])

DatabaseSession = Annotated[Session, Depends(get_db)]


@router.post(
    "",
    response_model=TransactionProcessResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_transaction(
    payload: TransactionCreate,
    db: DatabaseSession,
    current_user: User = Depends(get_current_user),
) -> TransactionProcessResponse:
    try:
        result = process_transaction(db, current_user, payload)
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        )

    return TransactionProcessResponse(
        transaction=result.transaction,
        alert_generated=bool(result.alert_ids),
        alert_ids=result.alert_ids,
        triggered_rules=result.triggered_rules,
    )


@router.get("", response_model=TransactionListResponse)
def get_transactions(
    db: DatabaseSession,
    current_user: User = Depends(get_current_user),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    transaction_reference: str | None = None,
    transaction_type: str | None = None,
    location: str | None = None,
    status_filter: TransactionStatus | None = Query(default=None, alias="status"),
    fraud_status: FraudStatus | None = None,
    min_amount: Decimal | None = Query(default=None, ge=0),
    max_amount: Decimal | None = Query(default=None, ge=0),
    start_date: datetime | None = None,
    end_date: datetime | None = None,
) -> TransactionListResponse:
    items, total = list_transactions(
        db,
        current_user,
        page=page,
        page_size=page_size,
        transaction_reference=transaction_reference,
        transaction_type=transaction_type,
        location=location,
        status=status_filter,
        fraud_status=fraud_status,
        min_amount=min_amount,
        max_amount=max_amount,
        start_date=start_date,
        end_date=end_date,
    )

    return TransactionListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=calculate_total_pages(total, page_size),
    )


@router.get("/search", response_model=TransactionListResponse)
def search_transactions(
    db: DatabaseSession,
    current_user: User = Depends(get_current_user),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    transaction_reference: str | None = None,
    transaction_type: str | None = None,
    location: str | None = None,
    status_filter: TransactionStatus | None = Query(default=None, alias="status"),
    fraud_status: FraudStatus | None = None,
    min_amount: Decimal | None = Query(default=None, ge=0),
    max_amount: Decimal | None = Query(default=None, ge=0),
    start_date: datetime | None = None,
    end_date: datetime | None = None,
) -> TransactionListResponse:
    return get_transactions(
        db=db,
        current_user=current_user,
        page=page,
        page_size=page_size,
        transaction_reference=transaction_reference,
        transaction_type=transaction_type,
        location=location,
        status_filter=status_filter,
        fraud_status=fraud_status,
        min_amount=min_amount,
        max_amount=max_amount,
        start_date=start_date,
        end_date=end_date,
    )


@router.get("/{transaction_id}", response_model=TransactionResponse)
def get_transaction(
    transaction_id: int,
    db: DatabaseSession,
    current_user: User = Depends(get_current_user),
) -> Transaction:
    transaction = get_transaction_by_id(db, current_user, transaction_id)

    if transaction is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found.",
        )

    return transaction
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.database.session import get_db
from app.reports.schemas import (
    ReportDetailResponse,
    ReportGenerateRequest,
    ReportListResponse,
)
from app.reports.service import (
    calculate_total_pages,
    generate_report,
    get_report_by_id,
    list_reports,
)
from app.users.models import User

router = APIRouter(prefix="/api/reports", tags=["reports"])

DatabaseSession = Annotated[Session, Depends(get_db)]


@router.post(
    "/generate",
    response_model=ReportDetailResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_report(
    payload: ReportGenerateRequest,
    db: DatabaseSession,
    current_user: User = Depends(get_current_user),
) -> ReportDetailResponse:
    return generate_report(db, current_user, payload)


@router.get("", response_model=ReportListResponse)
def get_reports(
    db: DatabaseSession,
    current_user: User = Depends(get_current_user),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
) -> ReportListResponse:
    items, total = list_reports(db, current_user, page, page_size)

    return ReportListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=calculate_total_pages(total, page_size),
    )


@router.get("/{report_id}", response_model=ReportDetailResponse)
def get_report(
    report_id: int,
    db: DatabaseSession,
    current_user: User = Depends(get_current_user),
) -> ReportDetailResponse:
    report = get_report_by_id(db, current_user, report_id)

    if report is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found.",
        )

    return report
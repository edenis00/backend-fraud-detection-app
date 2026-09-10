from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator


class ReportGenerateRequest(BaseModel):
    report_type: str = Field(
        default="transaction_analysis",
        min_length=3,
        max_length=100,
    )
    start_date: datetime
    end_date: datetime

    @model_validator(mode="after")
    def validate_reporting_period(self) -> "ReportGenerateRequest":
        if self.end_date <= self.start_date:
            raise ValueError("end_date must be later than start_date.")

        return self


class ReportListItemResponse(BaseModel):
    id: int
    report_type: str
    start_date: datetime
    end_date: datetime
    generated_by: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ReportDetailResponse(ReportListItemResponse):
    report_data: dict[str, Any]

    model_config = ConfigDict(from_attributes=True)


class ReportListResponse(BaseModel):
    items: list[ReportListItemResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
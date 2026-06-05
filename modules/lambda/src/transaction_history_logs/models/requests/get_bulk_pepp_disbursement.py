from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, model_validator
from utilities.date_filter import parse_date_filter


class GetBulkPeppDisbursementRequest(BaseModel):
    limit: int = Field(..., description="Number of records to return per page")
    cursor: Optional[str] = None
    accountNumbers: Optional[List[str]] = None
    status: Optional[List[str]] = None
    fileId: Optional[List[str]] = None
    transactionTypes: Optional[List[str]] = None
    fromDate: Optional[str] = None
    toDate: Optional[str] = None

    @model_validator(mode="after")
    def validate_date_range(self):
        today = datetime.today().date()

        if self.cursor == "":
            self.cursor = None
        if self.fromDate == "":
            self.fromDate = None
        if self.toDate == "":
            self.toDate = None

        if self.fromDate:
            from_dt = parse_date_filter(self.fromDate)
            if from_dt.date() > today:
                raise ValueError("fromDate must not be greater than today's date.")

        if self.toDate:
            to_dt = parse_date_filter(self.toDate)
            if to_dt.date() > today:
                raise ValueError("toDate must not be greater than today's date.")

        if self.fromDate and self.toDate:
            if from_dt > to_dt:
                raise ValueError("fromDate must not be greater than toDate")
            delta_days = (to_dt.date() - from_dt.date()).days
            if delta_days > 90:
                raise ValueError("For transaction history beyond T-90 days, please contact Customer Support.")

        return self

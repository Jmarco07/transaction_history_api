from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, model_validator


class GetPesonetTransactionRequest(BaseModel):
    limit: int = Field(..., description="Number of records to return per page")
    cursor: Optional[str] = None
    accountNumber: Optional[str] = None
    status: Optional[str] = None
    fromDate: Optional[str] = None
    toDate: Optional[str] = None

    @model_validator(mode="after")
    def validate_date_range(self):
        today = datetime.today().date()

        if self.cursor == "":
            self.cursor = None
        if self.accountNumber == "":
            self.accountNumber = None
        if self.status == "":
            self.status = None
        if self.fromDate == "":
            self.fromDate = None
        if self.toDate == "":
            self.toDate = None

        if self.fromDate:
            try:
                from_dt = datetime.strptime(self.fromDate, "%Y-%m-%d").date()
            except ValueError:
                raise ValueError("Invalid fromDate format, must be YYYY-MM-DD")
            if from_dt > today:
                raise ValueError("fromDate must not be greater than today's date.")

        if self.toDate:
            try:
                to_dt = datetime.strptime(self.toDate, "%Y-%m-%d").date()
            except ValueError:
                raise ValueError("Invalid toDate format, must be YYYY-MM-DD")
            if to_dt > today:
                raise ValueError("toDate must not be greater than today's date.")

        if self.fromDate and self.toDate:
            if from_dt > to_dt:
                raise ValueError("fromDate must not be greater than toDate")
            delta_days = (to_dt - from_dt).days
            if delta_days > 90:
                raise ValueError("For transaction history beyond T-90 days, please contact Customer Support.")

        return self

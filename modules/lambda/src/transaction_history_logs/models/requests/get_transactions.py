from datetime import datetime, timedelta
from typing import Literal, Optional, List
from pydantic import BaseModel, Field
from pydantic.functional_validators import AfterValidator
from typing_extensions import Annotated
from handlers.defaults.top_level import app

date_today = datetime.today()

AGENT_ORDER_BY = ["trxndate", "trxntypeno", "amount"]
PARTNER_ORDER_BY = ["uploaded_date", "trxn_amt", "transactionType"]

ALLOWED_FIELDS = {
    "corporate": {"type", "retRefNo", "transactionType", "status",
        "startDate", "end_date", "offset", "limit", "sort", "orderBy"},
    "agent": {"type", "retRefNo", "processedBy", "transactionType",
        "serviceType", "traceNo", "amount", "status",
        "startDate", "end_date", "offset", "limit", "sort", "orderBy"},
}

def check_order_by(value, info):
    values = info.data
    user_type = values.get("type")
    if not user_type:
        return value

    data_keys = {k for k, v in values.items() if v is not None}
    disallowed = data_keys - ALLOWED_FIELDS[user_type]
    if disallowed:
        raise ValueError(
            f"Invalid filters for type '{user_type}': {', '.join(disallowed)}"
        )

    if not value:
        value = "uploaded_date" if user_type == "corporate" else "trxndate"

    valid_order_by = PARTNER_ORDER_BY if user_type == "corporate" else AGENT_ORDER_BY
    if value not in valid_order_by:
        raise ValueError(
            f"Invalid orderBy value for type '{user_type}'. "
            f"Allowed values: {', '.join(valid_order_by)}"
        )

    return value


def get_90_days_ago(date=None) -> str:
    if date is None:
        date = date_today
    return (date - timedelta(days=90)).strftime("%Y-%m-%d")

def check_90_day_limit(string_date):
    if isinstance(string_date, datetime):
        date = string_date
    else:
        date = datetime.strptime(string_date, "%Y-%m-%d")

    if date.date() > date_today.date():
        raise ValueError("start date or end date must not be greater than today's date.")
    delta_days = (date_today - date).days
    assert delta_days <= 90, "For transaction history beyond T-90 days, please contact Customer Support."
    return string_date

def check_start_and_end_date(string_date, info):
    body = info.context.get("body", {})
    end_date_str = body.get("end_date")
    if not end_date_str:
        return string_date

    try:
        start_dt = (
            string_date.date()
            if isinstance(string_date, datetime)
            else datetime.strptime(string_date, "%Y-%m-%d").date()
        )
    except ValueError:
        raise ValueError(f"Invalid startDate format: '{string_date}', must be YYYY-MM-DD")

    try:
        end_dt = (
            end_date_str.date()
            if isinstance(end_date_str, datetime)
            else datetime.strptime(end_date_str, "%Y-%m-%d").date()
        )
    except ValueError:
        return string_date

    if start_dt > end_dt:
        raise ValueError("start date must not be greater than end date")

    return string_date



class GetTransactionsRequest(BaseModel):
    type: Literal["corporate", "agent"]
    retRefNo: Optional[List[str]] = None
    processedBy: Optional[List[str]] = None
    transactionType: Optional[List[str]] = None
    serviceType: Optional[List[str]] = None
    traceNo: Optional[List[str]] = None
    amount: Optional[List[str]] = None
    status: Optional[List[str]] = None

    startDate: Annotated[
        str,
        AfterValidator(check_90_day_limit),
        AfterValidator(check_start_and_end_date),
    ] = Field(
        default_factory=get_90_days_ago,
        pattern=r"\d{4}-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])",
    )
    offset: int = Field(default=1)
    limit: int = Field(default=5000)
    orderBy: Annotated[Optional[str], AfterValidator(check_order_by)] = None
    sort: Literal["ASC", "DESC"] = Field(default="DESC")
    end_date: Annotated[str, AfterValidator(check_90_day_limit)] = Field(
        default_factory=lambda: (datetime.today() - timedelta(days=1)).strftime("%Y-%m-%d"),
        pattern=r"\d{4}-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])",
    )

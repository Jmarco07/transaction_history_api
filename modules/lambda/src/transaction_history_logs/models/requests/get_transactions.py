from datetime import datetime, timedelta
from typing import Literal, Optional, List
from pydantic import BaseModel, Field
from pydantic.functional_validators import AfterValidator
from typing_extensions import Annotated
from handlers.defaults.top_level import app
from utilities.date_filter import parse_date_filter

date_today = datetime.today()

AGENT_ORDER_BY = ["trxndate", "trxntypeno", "amount"]

ALLOWED_FIELDS = {
    "agent": {"type", "retRefNo", "processedBy", "transactionType",
        "serviceType", "traceNo", "amount", "status",
        "startDate", "end_date", "cursor", "limit", "sort", "orderBy", "id"},
    "user": {"type", "retRefNo", "processedBy", "transactionType",
        "serviceType", "traceNo", "amount", "status",
        "startDate", "end_date", "cursor", "limit", "sort", "orderBy", "id"},
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
        value = "trxndate"

    valid_order_by = AGENT_ORDER_BY
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

def check_date_not_future(string_date):
    dt = parse_date_filter(string_date) if isinstance(string_date, str) else string_date
    if dt.date() > date_today.date():
        raise ValueError("start date or end date must not be greater than today's date.")
    return string_date

def check_start_and_end_date(string_date, info):
    body = info.context.get("body", {})
    end_date_str = body.get("end_date")
    if not end_date_str:
        return string_date

    try:
        start_dt = parse_date_filter(string_date)
    except ValueError:
        raise ValueError(f"Invalid startDate format: '{string_date}', must be YYYY-MM-DD or YYYY-MM-DD HH:MM:SS")

    try:
        end_dt = parse_date_filter(end_date_str)
    except ValueError:
        return string_date

    if start_dt > end_dt:
        raise ValueError("start date must not be greater than end date")

    delta_days = (end_dt.date() - start_dt.date()).days
    if delta_days > 90:
        raise ValueError("For transaction history beyond T-90 days, please contact Customer Support.")

    return string_date



class GetTransactionsRequest(BaseModel):
    type: Literal["agent", "user"]
    id: Optional[List[str]] = None
    retRefNo: Optional[List[str]] = None
    processedBy: Optional[List[str]] = None
    transactionType: Optional[List[str]] = None
    serviceType: Optional[List[str]] = None
    traceNo: Optional[List[str]] = None
    amount: Optional[List[str]] = None
    status: Optional[List[str]] = None

    startDate: Annotated[
        str,
        AfterValidator(check_date_not_future),
        AfterValidator(check_start_and_end_date),
    ] = Field(
        default_factory=get_90_days_ago,
    )
    cursor: Optional[str] = None
    limit: int = Field(default=5000)
    orderBy: Annotated[Optional[str], AfterValidator(check_order_by)] = None
    sort: Literal["ASC", "DESC"] = Field(default="DESC")
    end_date: Annotated[str, AfterValidator(check_date_not_future)] = Field(
        default_factory=lambda: (datetime.today() - timedelta(days=1)).strftime("%Y-%m-%d"),
    )

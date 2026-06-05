from datetime import datetime, timezone, timedelta

GMT_PLUS_8 = timezone(timedelta(hours=8))


def parse_date_filter(value: str) -> datetime:
    value = value.strip()

    # Handle ISO 8601 with timezone offset (e.g. 2026-03-02T17:22:11+08:00)
    if "T" in value:
        try:
            dt = datetime.fromisoformat(value)
            if dt.tzinfo is not None:
                return dt.astimezone(GMT_PLUS_8).replace(tzinfo=None)
            return dt
        except ValueError:
            pass

    for fmt in ["%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d"]:
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            continue

    raise ValueError(f"Invalid date format: '{value}'. Must be YYYY-MM-DD, YYYY-MM-DD HH:MM:SS, or ISO 8601 with timezone")


def has_time(value: str) -> bool:
    value = value.strip()
    return " " in value or "T" in value


def to_start_of_day(value: str) -> str:
    value = value.strip()
    dt = parse_date_filter(value)
    if has_time(value):
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    return f"{dt.strftime('%Y-%m-%d')} 00:00:00"


def to_end_of_day(value: str) -> str:
    value = value.strip()
    dt = parse_date_filter(value)
    if has_time(value):
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    return f"{dt.strftime('%Y-%m-%d')} 23:59:59"


def to_start_of_day_us(value: str) -> str:
    """Convert to MM/DD/YYYY HH:MM:SS AM/PM format for US-style date columns."""
    value = value.strip()
    dt = parse_date_filter(value)
    if not has_time(value):
        dt = dt.replace(hour=0, minute=0, second=0)
    return dt.strftime("%m/%d/%Y %I:%M:%S %p")


def to_end_of_day_us(value: str) -> str:
    """Convert to MM/DD/YYYY HH:MM:SS AM/PM format for US-style date columns."""
    value = value.strip()
    dt = parse_date_filter(value)
    if not has_time(value):
        dt = dt.replace(hour=23, minute=59, second=59)
    return dt.strftime("%m/%d/%Y %I:%M:%S %p")

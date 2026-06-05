from datetime import datetime, timezone, timedelta

GMT_PLUS_8 = timezone(timedelta(hours=8))

DATE_FORMATS = [
    "%m/%d/%Y %I:%M:%S.%f %p",
    "%m/%d/%Y %I:%M:%S %p",
    "%Y-%m-%d %H:%M:%S.%f",
    "%Y-%m-%d %H:%M:%S",
    "%Y-%m-%dT%H:%M:%S.%f",
    "%Y-%m-%dT%H:%M:%S",
    "%m/%d/%Y %H:%M:%S",
    "%m/%d/%Y",
    "%Y-%m-%d",
]


def to_gmt8(value) -> str | None:
    if value is None or value == "":
        return value

    if isinstance(value, datetime):
        if value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)
        return value.astimezone(GMT_PLUS_8).isoformat()

    if not isinstance(value, str):
        return value

    # Strip trailing nanosecond zeros (DB returns 9 fractional digits, Python supports 6)
    cleaned = value.strip()
    for fmt in DATE_FORMATS:
        try:
            # Handle nanoseconds by truncating to microseconds
            parse_value = cleaned
            if "." in parse_value and ("AM" in parse_value.upper() or "PM" in parse_value.upper()):
                parts = parse_value.split(".")
                frac_and_rest = parts[1].split(" ", 1)
                frac = frac_and_rest[0][:6]
                rest = frac_and_rest[1] if len(frac_and_rest) > 1 else ""
                parse_value = f"{parts[0]}.{frac} {rest}".strip()

            dt = datetime.strptime(parse_value, fmt)
            # Assume the date from DB is already in GMT+8 (Asia/Manila)
            dt = dt.replace(tzinfo=GMT_PLUS_8)
            return dt.isoformat()
        except (ValueError, IndexError):
            continue

    return value

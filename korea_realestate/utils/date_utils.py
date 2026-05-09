from datetime import date
from typing import Iterator


def to_year_month(value: str) -> str:
    """
    Normalize a year-month string to YYYYMM format.
    Accepts: '2024-01', '202401', '2024/01'.
    """
    cleaned = value.replace("-", "").replace("/", "")
    if len(cleaned) != 6 or not cleaned.isdigit():
        raise ValueError(f"Invalid year-month format: '{value}'. Expected YYYYMM or YYYY-MM.")
    return cleaned


def iter_months(start_ym: str, end_ym: str) -> Iterator[str]:
    """Yield YYYYMM strings from start to end inclusive."""
    start = to_year_month(start_ym)
    end = to_year_month(end_ym)

    year, month = int(start[:4]), int(start[4:])
    end_year, end_month = int(end[:4]), int(end[4:])

    while (year, month) <= (end_year, end_month):
        yield f"{year:04d}{month:02d}"
        month += 1
        if month > 12:
            month = 1
            year += 1


def current_year_month() -> str:
    today = date.today()
    return f"{today.year:04d}{today.month:02d}"

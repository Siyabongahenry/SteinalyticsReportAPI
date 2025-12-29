from datetime import date, datetime
import holidays

# South African public holidays (observed = Sunday → Monday)
ZA_HOLIDAYS = holidays.country_holidays("ZA", observed=True)


def _parse_date(input_date: date | str) -> date:
    """
    Internal helper to normalize input into a date object.
    """
    if isinstance(input_date, str):
        return datetime.strptime(input_date, "%Y-%m-%d").date()
    return input_date


def get_weekday_number(input_date: date | str) -> int:
    """
    Returns weekday number:
    Monday = 0 ... Sunday = 6
    """
    d = _parse_date(input_date)
    return d.weekday()


def is_public_holiday(input_date: date | str) -> bool:
    """
    Returns True if the date is a South African public holiday,
    otherwise False.
    Observed holidays are handled automatically.
    """
    d = _parse_date(input_date)
    return d in ZA_HOLIDAYS

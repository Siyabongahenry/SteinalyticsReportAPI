import pytest
from datetime import date

from app.utils.date_utils import (
    _parse_date,
    get_weekday_number,
    is_public_holiday,
)

def test_parse_date_from_string():
    result = _parse_date("2024-01-01")
    assert result == date(2024, 1, 1)


def test_parse_date_from_date():
    d = date(2024, 1, 1)
    result = _parse_date(d)
    assert result is d

def test_get_weekday_number_from_date():
    # Monday
    assert get_weekday_number(date(2024, 1, 1)) == 0


def test_get_weekday_number_from_string():
    # Sunday
    assert get_weekday_number("2024-01-07") == 6


def test_is_public_holiday_true():
    # New Year's Day (South Africa)
    assert is_public_holiday("2024-01-01") is True


def test_is_public_holiday_false():
    assert is_public_holiday("2024-01-02") is False

def test_observed_public_holiday():
    # Human Rights Day 2021-03-21 (Sunday)
    # Observed on Monday 2021-03-22
    assert is_public_holiday("2021-03-22") is True

def test_parse_date_invalid_format():
    with pytest.raises(ValueError):
        _parse_date("01-01-2024")

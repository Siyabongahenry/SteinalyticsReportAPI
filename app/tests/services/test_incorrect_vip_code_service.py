import json
import pandas as pd
import pytest
from pathlib import Path
from app.services.incorrect_vip_service import IncorrectVIPService

# --- Fixtures ---
@pytest.fixture
def config_file(tmp_path):
    rules = {
        "hour_codes": {
            "mon_fri_normal": [100],
            "mon_fri_overtime": [200],
            "saturday_overtime": [300],
            "sunday_overtime": [400],
            "holiday_normal": [500],
            "holiday_overtime": [600],
        }
    }
    path = tmp_path / "rules.json"
    path.write_text(json.dumps(rules))
    return path


@pytest.fixture
def sample_df():
    return pd.DataFrame({
        "Resource no.": [1, 2, 3, 4],
        "Work date": ["2025-01-06", "2025-01-11", "2025-01-12", "2025-01-01"],  # Mon, Sat, Sun, Holiday
        "VIP Code": [100, 999, 400, 999],  # valid weekday, invalid Saturday, valid Sunday, invalid Holiday
    })


# --- Tests ---
def test_find_incorrect_vip(config_file, sample_df, monkeypatch):
    # Patch date_utils functions
    from app.utils import date_utils

    monkeypatch.setattr(date_utils, "get_weekday_number", lambda d: pd.to_datetime(d).weekday())
    monkeypatch.setattr(date_utils, "is_public_holiday", lambda d: pd.to_datetime(d).strftime("%m-%d") == "01-01")

    service = IncorrectVIPService(sample_df.copy(), str(config_file))
    result = service.find_incorrect_vip()

    # Expect rows 2 (Saturday invalid) and 4 (Holiday invalid)
    assert set(result["Resource no."]) == {2, 4}
    assert "VIP Code" in result.columns
    assert "_weekday" not in result.columns
    assert "_is_holiday" not in result.columns


def test_valid_codes_pass(config_file, monkeypatch):
    df = pd.DataFrame({
        "Resource no.": [1, 2],
        "Work date": ["2025-01-06", "2025-01-12"],  # Monday, Sunday
        "VIP Code": [100, 400],  # valid weekday and valid Sunday
    })

    from app.utils import date_utils
    monkeypatch.setattr(date_utils, "get_weekday_number", lambda d: pd.to_datetime(d).weekday())
    monkeypatch.setattr(date_utils, "is_public_holiday", lambda d: False)

    service = IncorrectVIPService(df.copy(), str(config_file))
    result = service.find_incorrect_vip()

    # No incorrect rows expected
    assert result.empty


def test_invalid_type_casting(config_file, monkeypatch):
    df = pd.DataFrame({
        "Resource no.": [1],
        "Work date": ["2025-01-06"],
        "VIP Code": ["999"],  # string, should cast to int
    })

    from app.utils import date_utils
    monkeypatch.setattr(date_utils, "get_weekday_number", lambda d: pd.to_datetime(d).weekday())
    monkeypatch.setattr(date_utils, "is_public_holiday", lambda d: False)

    service = IncorrectVIPService(df.copy(), str(config_file))
    result = service.find_incorrect_vip()

    # Should detect incorrect VIP code
    assert not result.empty
    assert result.iloc[0]["VIP Code"] == 999

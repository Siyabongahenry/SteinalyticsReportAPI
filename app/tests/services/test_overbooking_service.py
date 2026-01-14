import pandas as pd
import pytest
from app.services.overbooking_service import OverbookingService   # adjust import path


@pytest.fixture
def sample_df():
    return pd.DataFrame({
        "Resource no.": [1, 1, 1, 2, 2, 2],
        "Work date": [
            "2025-01-05", "2025-01-05", "2025-01-05",  # Sunday
            "2025-01-06", "2025-01-06", "2025-01-06"   # Monday
        ],
        "VIP Code": [101, 101, 201, 201, 201, 201],   # 101 overtime, 201 normal
        "Hours worked": [2, 2, 4, 5, 5, 5]
    })


def test_find_duplicates_overtime(sample_df):
    service = OverbookingService(sample_df.copy())
    result = service.find_duplicates_overtime()

    # Expect duplicate overtime entries (VIP Code 101 on 2025-01-05)
    assert not result.empty
    assert all(result["VIP Code"] == 101)
    assert set(result["Resource no."]) == {1}


def test_find_overbooked_normal_daily(sample_df):
    service = OverbookingService(sample_df.copy())
    result = service.find_overbooked_normal_daily()

    # Monday requires 8.75 hours, but resource 2 has 15 total
    assert not result.empty
    assert set(result["Resource no."]) == {2}
    assert all(result["cum_sum"] > result["required_norm"])


def test_no_duplicates():
    df = pd.DataFrame({
        "Resource no.": [1, 2],
        "Work date": ["2025-01-06", "2025-01-06"],
        "VIP Code": [101, 201],
        "Hours worked": [2, 8]
    })
    service = OverbookingService(df)
    result = service.find_duplicates_overtime()

    # No duplicates expected
    assert result.empty


def test_no_overbooking():
    df = pd.DataFrame({
        "Resource no.": [1],
        "Work date": ["2025-01-06"],  # Monday
        "VIP Code": [201],            # normal code
        "Hours worked": [8]           # below 8.75
    })
    service = OverbookingService(df)
    result = service.find_overbooked_normal_daily()

    # No overbooking expected
    assert result.empty

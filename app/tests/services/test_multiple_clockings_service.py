import pandas as pd
import pytest
from app.services.multiple_clockings_service import MultipleClockingsService   # adjust import path


@pytest.fixture
def sample_df():
    return pd.DataFrame({
        "Clock No.": [1, 1, 1, 1, 2, 2, 2],
        "Date": ["2025-01-01"] * 4 + ["2025-01-02"] * 3,
        "Employee": ["A", "B", "C", "D", "E", "F", "G"]
    })


def test_get_multiple_clockings_returns_rows(sample_df):
    service = MultipleClockingsService(sample_df.copy())
    result = service.getMultipleClockings()

    # Clock No. 1 on 2025-01-01 appears 4 times, so all 4 should be returned
    assert len(result) == 4
    assert set(result["Clock No."]) == {1}
    assert set(result["Date"]) == {"2025-01-01"}


def test_no_multiple_clockings():
    df = pd.DataFrame({
        "Clock No.": [1, 1, 2, 2, 3],
        "Date": ["2025-01-01", "2025-01-01", "2025-01-02", "2025-01-02", "2025-01-03"],
        "Employee": ["A", "B", "C", "D", "E"]
    })
    service = MultipleClockingsService(df)
    result = service.getMultipleClockings()

    # No group exceeds 3, so result should be empty
    assert result.empty


def test_mixed_groups():
    df = pd.DataFrame({
        "Clock No.": [1, 1, 1, 1, 2, 2],
        "Date": ["2025-01-01"] * 4 + ["2025-01-02"] * 2,
        "Employee": ["A", "B", "C", "D", "E", "F"]
    })
    service = MultipleClockingsService(df)
    result = service.getMultipleClockings()

    # Only Clock No. 1 group should be returned
    assert set(result["Clock No."]) == {1}
    assert len(result) == 4

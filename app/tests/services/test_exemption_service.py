import pandas as pd
import pytest
from pandas.testing import assert_frame_equal
from app.services.exemption_service import ExemptionService   # adjust import path


@pytest.fixture
def sample_df():
    # Create sample data with >72 hours in one week
    data = {
        "Resource no.": [101, 101, 101, 102],
        "Work date": ["2025-01-05", "2025-01-06", "2025-01-07", "2025-01-08"],  # same week
        "Hours worked": [30, 30, 20, 80],  # 101 has 80 total, 102 has 80
    }
    return pd.DataFrame(data)


def test_get_week_exemption(sample_df):
    service = ExemptionService(sample_df.copy(), type="week")
    result = service.get_week_exemption()

    # Expected: both employees exceed 72 hours
    assert set(result["Resource no."]) == {101, 102}
    assert all(result["Exemption"] == 72)
    assert all(result["Excess"] > 0)


def test_get_month_exemption(sample_df):
    service = ExemptionService(sample_df.copy(), type="month")
    result = service.get_month_exemption()

    # Expected: both employees aggregated into January 2025
    assert set(result["Resource no."]) == {101, 102}
    assert set(result["Month"]) == {"2025.01"}
    assert all(result["Exemption"] == 72)
    # Excess should equal weekly excess summed (both >0)
    assert all(result["Excess"] > 0)


def test_get_exemption_week(sample_df):
    service = ExemptionService(sample_df.copy(), type="week")
    result = service.get_exemption()
    assert "Week" in result.columns


def test_get_exemption_month(sample_df):
    service = ExemptionService(sample_df.copy(), type="month")
    result = service.get_exemption()
    assert "Month" in result.columns


def test_invalid_type_raises(sample_df):
    service = ExemptionService(sample_df.copy(), type="year")
    with pytest.raises(ValueError, match="Type must be 'week' or 'month'"):
        service.get_exemption()

import pandas as pd
import pytest
from app.services.productivity_report_service import ProductivityReportService   # adjust import path


@pytest.fixture
def df_hours_worked():
    return pd.DataFrame({
        "Resource no.": [1, 1, 2],
        "Work date": ["2025-01-05", "2025-01-05", "2025-01-06"],
        "VIP Code": [100, 111, 200],   # 200 not productive
        "Hours worked": [5, 4, 8]
    })


@pytest.fixture
def df_hours_posted():
    return pd.DataFrame({
        "User Originator": ["clerk1", "clerk1", "clerk2", "clerk2"],
        "Posting Date": ["2025-01-05", "2025-01-05", "2025-01-06", "2025-01-06"],
        "VIP Code": [100, 101, 900, 111],   # mix of productive + allowance
        "Entry No.": [1, 2, 3, 4]
    })


def test_hours_worked_by_clerk(df_hours_worked, df_hours_posted):
    service = ProductivityReportService(df_hours_worked, df_hours_posted)
    result = service.hours_worked_by_clerk()

    # Only VIP codes 100 and 111 should be included
    assert set(result["Resource no."]) == {1}
    assert result["Hours worked"].sum() == 9


def test_productive_hours_posted(df_hours_worked, df_hours_posted):
    service = ProductivityReportService(df_hours_worked, df_hours_posted)
    result = service.productive_hours_posted()

    # Only productive codes (100, 111) should be counted
    assert set(result["User Originator"]) == {"clerk1", "clerk2"}
    assert result["Entries posted"].sum() == 2


def test_allowance_posted(df_hours_worked, df_hours_posted):
    service = ProductivityReportService(df_hours_worked, df_hours_posted)
    result = service.allowance_posted()

    # Should include VIP Code 101 and >=900
    assert set(result["User Originator"]) == {"clerk1", "clerk2"}
    assert result["Entries posted"].sum() == 2


def test_get_summary(df_hours_worked, df_hours_posted):
    service = ProductivityReportService(df_hours_worked, df_hours_posted)
    summary = service.get_summary()

    # Ensure summary has both columns
    assert "Hours worked" in summary.columns
    assert "Entries posted" in summary.columns

    # Check that totals are aggregated correctly
    assert summary["Hours worked"].sum() == 9
    assert summary["Entries posted"].sum() == 4

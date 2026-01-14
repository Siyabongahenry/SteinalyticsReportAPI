import pandas as pd
import pytest
from app.services.attendence_service import AttendanceService

@pytest.fixture
def sample_df():
    data = {
        "WTT": ["SiteA", "SiteA", "SiteA", "SiteB", "SiteB", "SiteB"],
        "Date": [
            "2024-01-01", "2024-01-01", "2024-01-02",
            "2024-01-01", "2024-01-02", "2024-01-02"
        ],
        "Clock No.": [101, 101, 102, 201, 201, 202],
    }
    return pd.DataFrame(data)

@pytest.fixture
def service(sample_df):
    return AttendanceService(sample_df)

def test_get_employees_list(service):
    result = service.get_employees_list()
    # Should remove duplicate scans (Clock No. 101 on SiteA 2024-01-01)
    assert len(result) == 5
    assert set(result["Clock No."]) == {101, 102, 201, 202}

def test_get_summary_by_site(service):
    result = service.get_summary_by_site()
    # SiteA 2024-01-01 has only 1 unique employee (101)
    siteA_day1 = result[(result["WTT"] == "SiteA") & (result["Date"] == "2024-01-01")]
    assert siteA_day1["attendance"].iloc[0] == 1

    # SiteB 2024-01-02 has 2 unique employees (201, 202)
    siteB_day2 = result[(result["WTT"] == "SiteB") & (result["Date"] == "2024-01-02")]
    assert siteB_day2["attendance"].iloc[0] == 2

def test_get_attendance_by_employee_week(service):
    result = service.get_attendance_by_employee_week()
    # Employee 101 attended 2 days in the same week
    emp101 = result[result["Clock No."] == 101]
    assert emp101["attendance_days"].iloc[0] == 2

def test_get_attendance_by_employee_month(service):
    result = service.get_attendance_by_employee_month()
    # Employee 201 attended 2 days in January 2024
    emp201 = result[result["Clock No."] == 201]
    assert emp201["attendance_days"].iloc[0] == 2

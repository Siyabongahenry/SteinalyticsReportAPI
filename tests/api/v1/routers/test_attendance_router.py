import io
import pandas as pd
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

# Helper: create a sample Excel file in memory
def create_sample_excel():
    df = pd.DataFrame({
        "Clock No.": [101, 102, 101],
        "Date": ["2024-01-01", "2024-01-01", "2024-01-01"],
        "WTT": ["SiteA", "SiteA", "SiteA"],
    })
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df.to_excel(writer, index=False)
    buffer.seek(0)
    return buffer.read()

@pytest.fixture
def sample_file():
    return create_sample_excel()

def test_attendance_list(sample_file):
    response = client.post(
        "/attendance/list",
        files={"file": ("test.xlsx", sample_file, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
    )
    assert response.status_code == 200
    data = response.json()
    assert "download_url" in data

def test_site_summary(sample_file):
    response = client.post(
        "/attendance/site-summary",
        files={"file": ("test.xlsx", sample_file, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
    )
    assert response.status_code == 200
    data = response.json()
    assert "download_url" in data

def test_employee_attendance_summary(sample_file):
    response = client.post(
        "/attendance/employee-attendance-summary",
        files={"file": ("test.xlsx", sample_file, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
    )
    assert response.status_code == 200
    data = response.json()
    assert "download_url" in data

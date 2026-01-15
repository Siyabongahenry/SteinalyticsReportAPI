import io
import pandas as pd
import pytest
from fastapi.testclient import TestClient
from app.main import app  # assuming your FastAPI app is defined in app/main.py

client = TestClient(app)

# Helper: create an Excel file in memory
def create_excel_file(df: pd.DataFrame) -> bytes:
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df.to_excel(writer, index=False)
    buffer.seek(0)
    return buffer.read()

@pytest.fixture
def sample_file():
    df = pd.DataFrame({
        "Entry No.": [1, 2, 3],
        "Resource no.": ["R001", "R002", "R003"],
        "VIP Code": ["VIP", "VIP", "VIP"],
        "Hours worked": [8, 7, 6],
        "Applies-To Entry": ["", "", ""],
    })
    return create_excel_file(df)

def test_productivity_report(sample_file):
    response = client.post(
        "/productivity-report",
        files={"file": ("test.xlsx", sample_file, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
    )
    assert response.status_code == 200
    data = response.json()

    # Basic response checks
    assert "summary" in data
    assert "download_url" in data

    # Validate summary structure (depends on ProductivityReportService.get_summary output)
    summary = data["summary"]
    assert isinstance(summary, list) or isinstance(summary, dict)

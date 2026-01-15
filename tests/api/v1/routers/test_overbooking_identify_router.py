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
def file_with_issues():
    # Example: duplicate overtime and overbooked hours
    df = pd.DataFrame({
        "Entry No.": [1, 2, 3],
        "Resource no.": ["R001", "R001", "R002"],
        "VIP Code": ["VIP", "VIP", "VIP"],
        "Hours worked": [10, 10, 15],  # duplicate overtime + overbooked daily
        "Applies-To Entry": ["", "", ""],
    })
    return create_excel_file(df)

@pytest.fixture
def file_without_issues():
    df = pd.DataFrame({
        "Entry No.": [1, 2],
        "Resource no.": ["R001", "R002"],
        "VIP Code": ["VIP", "VIP"],
        "Hours worked": [8, 7],  # normal hours, no duplicates
        "Applies-To Entry": ["", ""],
    })
    return create_excel_file(df)

def test_overbooking_with_issues(file_with_issues):
    response = client.post(
        "/overbooking",
        files={"file": ("test.xlsx", file_with_issues, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
    )
    assert response.status_code == 200
    data = response.json()
    assert "incorrect_rows" in data
    assert data["incorrect_rows"] > 0
    assert "download_url" in data

def test_overbooking_without_issues(file_without_issues):
    response = client.post(
        "/overbooking",
        files={"file": ("test.xlsx", file_without_issues, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "No duplicate or overbooked entries found"
    assert data["incorrect_rows"] == 0
    assert "download_url" not in data

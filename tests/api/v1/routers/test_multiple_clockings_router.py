import io
import pandas as pd
import pytest
from fastapi.testclient import TestClient
from app.main import app  # assuming your FastAPI app is defined in app/main.py

client = TestClient(app)

# Helper: create a sample Excel file in memory
def create_excel_file(df: pd.DataFrame) -> bytes:
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df.to_excel(writer, index=False)
    buffer.seek(0)
    return buffer.read()

@pytest.fixture
def file_with_multiple_clockings():
    df = pd.DataFrame({
        "Clock No.": [101, 101, 102],
        "Date": ["2024-01-01", "2024-01-01", "2024-01-01"],
    })
    return create_excel_file(df)

@pytest.fixture
def file_without_multiple_clockings():
    df = pd.DataFrame({
        "Clock No.": [101, 102, 103],
        "Date": ["2024-01-01", "2024-01-01", "2024-01-01"],
    })
    return create_excel_file(df)

def test_multiple_clockings_found(file_with_multiple_clockings):
    response = client.post(
        "/multiple-clockings",
        files={"file": ("test.xlsx", file_with_multiple_clockings, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
    )
    assert response.status_code == 200
    data = response.json()
    assert "multiple_clockings_count" in data
    assert data["multiple_clockings_count"] > 0
    assert "download_url" in data

def test_multiple_clockings_not_found(file_without_multiple_clockings):
    response = client.post(
        "/multiple-clockings",
        files={"file": ("test.xlsx", file_without_multiple_clockings, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Multiple clockings not found"
    assert data["multiple_clockings_count"] == 0
    assert "download_url" not in data

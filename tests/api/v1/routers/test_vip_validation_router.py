import io
import json
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
def file_with_incorrect_vip(tmp_path):
    # Example: VIP code not in config
    df = pd.DataFrame({
        "Entry No.": [1],
        "Resource no.": ["9000"],
        "VIP Code": ["900"],  # should trigger incorrect
        "Hours worked": [8.75],
        "Applies-To Entry": [""],
    })
    return create_excel_file(df)

@pytest.fixture
def file_with_correct_vip(tmp_path):
    # Example: VIP code matches config
    df = pd.DataFrame({
        "Entry No.": [1],
        "Resource no.": ["R001"],
        "VIP Code": ["VIP"],  # assume valid
        "Hours worked": [8],
        "Applies-To Entry": [""],
    })
    return create_excel_file(df)

def test_vip_validation_incorrect(file_with_incorrect_vip):
    response = client.post(
        "/vip-validation",
        files={"file": ("test.xlsx", file_with_incorrect_vip, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
    )
    assert response.status_code == 200
    data = response.json()
    assert "incorrect_rows" in data
    assert data["incorrect_rows"] > 0
    assert "download_url" in data

def test_vip_validation_correct(file_with_correct_vip):
    response = client.post(
        "/vip-validation",
        files={"file": ("test.xlsx", file_with_correct_vip, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "No incorrect VIP codes found"
    assert data["incorrect_rows"] == 0
    assert "download_url" not in data

import io
import pandas as pd
import pytest
from fastapi.testclient import TestClient
from app.main import app  # assuming your FastAPI app is defined in app/main.py

client = TestClient(app)

# Helper: create a sample Excel file in memory
def create_sample_excel(with_exemption=True):
    if with_exemption:
        df = pd.DataFrame({
            "Entry No.": [1, 2],
            "Resource no.": ["R001", "R002"],
            "VIP Code": ["VIP", "VIP"],
            "Hours worked": [50, 60],  # assume this triggers exemption
            "Applies-To Entry": ["", ""],
        })
    else:
        df = pd.DataFrame({
            "Entry No.": [1],
            "Resource no.": ["R001"],
            "VIP Code": ["VIP"],
            "Hours worked": [5],  # below exemption threshold
            "Applies-To Entry": [""],
        })

    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df.to_excel(writer, index=False)
    buffer.seek(0)
    return buffer.read()

@pytest.fixture
def exemption_file():
    return create_sample_excel(with_exemption=True)

@pytest.fixture
def no_exemption_file():
    return create_sample_excel(with_exemption=False)

def test_exemption_report_with_data(exemption_file):
    response = client.post(
        "/exemption",
        files={"file": ("test.xlsx", exemption_file, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
        data={"exemption_type": "weekly"}  # example type
    )
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Exemption report generated successfully"
    assert "download_url" in data

def test_exemption_report_no_data(no_exemption_file):
    response = client.post(
        "/exemption",
        files={"file": ("test.xlsx", no_exemption_file, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
        data={"exemption_type": "weekly"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "No exemption exceeded"
    assert "download_url" not in data

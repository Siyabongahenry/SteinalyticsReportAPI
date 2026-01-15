import io
import pandas as pd
import pytest
from fastapi.testclient import TestClient
from app.main import app  # assuming your FastAPI app is defined in app/main.py

client = TestClient(app)

# Helper: create a sample Excel file in memory
def create_sample_excel():
    df = pd.DataFrame({
        "MeterId": [1, 2, 1, 3],
        "Date": ["2024-01-01", "2024-01-01", "2024-01-02", "2024-01-01"],
    })
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df.to_excel(writer, index=False)
    buffer.seek(0)
    return buffer.read()

@pytest.fixture
def sample_file():
    return create_sample_excel()

def test_devices_count_endpoint(sample_file):
    response = client.post(
        "/device-clockings",
        files={"file": ("test.xlsx", sample_file, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
    )
    assert response.status_code == 200
    data = response.json()

    # Basic response checks
    assert "download_url" in data
    assert "data" in data

    # Validate returned data structure
    clockings_data = data["data"]
    assert isinstance(clockings_data, list) or isinstance(clockings_data, dict)
    # Depending on how DeviceService.clockings_count() structures output,
    # you can assert more specific conditions here.

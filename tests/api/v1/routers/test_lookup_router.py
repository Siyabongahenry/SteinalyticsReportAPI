import io
import pandas as pd
import pytest
from fastapi.testclient import TestClient
from app.main import app  # assuming your FastAPI app is defined in app/main.py

client = TestClient(app)

# Helper: create sample Excel files in memory
def create_excel_file(df: pd.DataFrame) -> bytes:
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df.to_excel(writer, index=False)
    buffer.seek(0)
    return buffer.read()

@pytest.fixture
def sample_files():
    df1 = pd.DataFrame({
        "ID": [1, 2, 3],
        "Name": ["Alice", "Bob", "Charlie"]
    })
    df2 = pd.DataFrame({
        "ID": [1, 2, 4],
        "Department": ["HR", "Finance", "IT"]
    })
    file1 = create_excel_file(df1)
    file2 = create_excel_file(df2)
    return [file1, file2]

def test_lookup_endpoint(sample_files):
    response = client.post(
        "/lookup",
        files=[
            ("files", ("report1.xlsx", sample_files[0], "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")),
            ("files", ("report2.xlsx", sample_files[1], "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")),
        ]
    )
    assert response.status_code == 200
    data = response.json()

    # Basic response checks
    assert "download_url" in data

    # Optional: inspect merged output if returned in response
    # (depends on whether LookupService.join_reports() returns JSON-serializable data)

import pytest
import pandas as pd
from io import BytesIO
from fastapi import HTTPException

from app.utils.excel_upload_utils import load_excel_file  # adjust import

@pytest.mark.asyncio
async def test_load_excel_file_success():
    df = pd.DataFrame({
        "name": ["Alice", "Bob"],
        "age": [30, 25],
    })

    buffer = BytesIO()
    df.to_excel(buffer, index=False, engine="openpyxl")
    contents = buffer.getvalue()

    required_columns = {"name", "age"}

    result = await load_excel_file(contents, required_columns)

    assert isinstance(result, pd.DataFrame)
    assert list(result.columns) == ["name", "age"]
    assert len(result) == 2

@pytest.mark.asyncio
async def test_load_excel_file_missing_columns():
    df = pd.DataFrame({
        "name": ["Alice"],
    })

    buffer = BytesIO()
    df.to_excel(buffer, index=False, engine="openpyxl")
    contents = buffer.getvalue()

    required_columns = {"name", "age"}

    with pytest.raises(HTTPException) as exc:
        await load_excel_file(contents, required_columns)

    assert exc.value.status_code == 400
    assert "Missing required columns" in exc.value.detail

import os
import pandas as pd
import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch
from app.core.settings import settings
from app.services.excel_export_service import ExcelExportService  # adjust import path


@pytest.fixture
def sample_sheets():
    return {
        "Sheet1": pd.DataFrame({"A": [1, 2], "B": [3, 4]}),
        "Sheet2": pd.DataFrame({"X": ["foo", "bar"], "Y": ["baz", "qux"]}),
    }


def test_upload_excel_local(tmp_path, sample_sheets):
    service = ExcelExportService(storage_backend="local", local_export_dir=tmp_path)

    file_path = service.upload_excel(sample_sheets, prefix="test_exports", filename_prefix="testfile")

    # Assert file exists
    assert Path(file_path).exists()
    assert file_path.endswith(".xlsx")


def test_upload_excel_empty_sheet_raises(tmp_path):
    service = ExcelExportService(storage_backend="local", local_export_dir=tmp_path)

    bad_sheets = {"EmptySheet": pd.DataFrame()}
    with pytest.raises(ValueError, match="has no data"):
        service.upload_excel(bad_sheets)


def test_upload_excel_no_sheets_raises(tmp_path):
    service = ExcelExportService(storage_backend="local", local_export_dir=tmp_path)

    with pytest.raises(ValueError, match="No sheets provided"):
        service.upload_excel({})


@patch("boto3.client")
def test_upload_excel_s3(mock_boto, sample_sheets):
    # Mock S3 client
    mock_s3 = MagicMock()
    mock_boto.return_value = mock_s3

    service = ExcelExportService(storage_backend="s3", bucket_name="fake-bucket", region="us-east-1")

    key = service.upload_excel(sample_sheets, prefix="exports", filename_prefix="testfile")

    # Assert S3 put_object was called
    assert mock_s3.put_object.called
    assert key.startswith("exports/testfile")
    assert key.endswith(".xlsx")


@patch("boto3.client")
def test_generate_presigned_url_s3(mock_boto):
    mock_s3 = MagicMock()
    mock_s3.generate_presigned_url.return_value = "http://fake-url"
    mock_boto.return_value = mock_s3

    service = ExcelExportService(storage_backend="s3", bucket_name="fake-bucket", region="us-east-1")

    url = service.generate_presigned_url("exports/test.xlsx")
    assert url == "http://fake-url"


def test_generate_presigned_url_local(tmp_path):
    service = ExcelExportService(storage_backend="local", local_export_dir=tmp_path)

    fake_file = tmp_path / "exports" / "test.xlsx"
    fake_file.parent.mkdir(parents=True, exist_ok=True)
    fake_file.write_text("dummy")

    url = service.generate_presigned_url(str(fake_file))
    assert url.startswith("file:///")
    assert "test.xlsx" in url

import pandas as pd
import pytest
from unittest.mock import patch, MagicMock

from app.services.excel_export_service import ExcelExportService
from app.utils.export_utils import export_excel_and_get_url  # adjust import path if needed


def test_export_excel_and_get_url():
    # Prepare sample DataFrame
    df = pd.DataFrame({"col1": [1, 2], "col2": ["a", "b"]})
    sheets = {"Sheet1": df}

    prefix = "test-prefix"
    filename_prefix = "test-file"

    # Mock ExcelExportService methods
    with patch.object(ExcelExportService, "upload_excel", return_value="mock-key") as mock_upload, \
         patch.object(ExcelExportService, "generate_presigned_url", return_value="http://mock-url") as mock_url:

        result = export_excel_and_get_url(
            sheets=sheets,
            prefix=prefix,
            filename_prefix=filename_prefix,
        )

        # Assertions
        mock_upload.assert_called_once_with(
            sheets=sheets,
            prefix=prefix,
            filename_prefix=filename_prefix,
        )
        mock_url.assert_called_once_with("mock-key")
        assert result == "http://mock-url"

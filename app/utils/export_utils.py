from typing import Dict
import pandas as pd
from app.services.excel_export_service import ExcelExportService


def export_excel_and_get_url(
    sheets: Dict[str, pd.DataFrame],
    *,
    prefix: str,
    filename_prefix: str,
    user_id: str
) -> Dict[str, str]:
    """
    Export one or more pandas DataFrames to an Excel file and return both
    the storage key and a download URL.

    :param sheets: Dictionary where:
                   - key   = Excel sheet name
                   - value = pandas DataFrame
    :param prefix: Folder path (S3 key prefix or local subfolder)
    :param filename_prefix: Prefix used when generating the Excel filename
    :param user_id: User identifier for namespacing
    :return: Dict with 'key' and 'download_url'
    """

    export_service = ExcelExportService()

    # Upload Excel file and receive storage key or file path
    key = export_service.upload_excel(
        sheets=sheets,
        prefix=prefix,
        filename_prefix=filename_prefix,
        user_id=user_id,
    )

    # Generate presigned URL (or local file URL)
    download_url = export_service.generate_presigned_url(key)

    return {
        "key": key,
        "download_url": download_url,
    }

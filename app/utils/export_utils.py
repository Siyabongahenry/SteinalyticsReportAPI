from typing import Dict
import pandas as pd
from app.services.excel_export_service import ExcelExportService


def export_excel_and_get_url(
    sheets: Dict[str, pd.DataFrame],
    *,
    prefix: str,
    filename_prefix: str,
    user_id
) -> str:
    """
    Export one or more pandas DataFrames to an Excel file and return a download URL.

    This function acts as a thin wrapper around ExcelExportService to:
    - Create the export service with the correct storage backend
    - Upload the Excel file (locally or to S3)
    - Generate a downloadable URL for the exported file

    :param sheets: Dictionary where:
                   - key   = Excel sheet name
                   - value = pandas DataFrame
    :param bucket_name: S3 bucket name (required when using S3 backend)
    :param storage_backend: Storage backend identifier ('s3' or 'local')
    :param prefix: Folder path (S3 key prefix or local subfolder)
    :param filename_prefix: Prefix used when generating the Excel filename
    :return: Download URL (presigned S3 URL or local file URL)
    """

    # Initialize the Excel export service
    export_service = ExcelExportService()

    # Upload Excel file and receive storage key or file path
    key = export_service.upload_excel(
        sheets=sheets,
        prefix=prefix,
        filename_prefix=filename_prefix,
        user_id = user_id
    )

    # Generate and return a downloadable URL for the exported file
    return export_service.generate_presigned_url(key)

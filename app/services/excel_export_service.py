import boto3
import uuid
import pandas as pd
from io import BytesIO
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Dict
from app.core.settings import settings


class ExcelExportService:
    """
    Service responsible for exporting pandas DataFrames to Excel files.

    Supports two storage backends:
    - Local filesystem
    - AWS S3

    Storage backend is controlled via:
    - Constructor argument `storage_backend`
    - OR environment variable `STORAGE_BACKEND` (defaults to 'local')
    """

    def __init__(
        self,
        bucket_name: Optional[str] = None,
        storage_backend: Optional[str] = None,
        region: Optional[str] = None,
        local_export_dir: str = "exports",
    ):
        """
        Initialize the export service.

        :param bucket_name: S3 bucket name (required if using S3)
        :param region: AWS region for S3
        :param storage_backend: 's3' or 'local'
        :param local_export_dir: Base directory for local exports
        """

        # Determine storage backend (env var takes fallback role)
        self.storage_backend = storage_backend or settings.storage_backend

        self.bucket_name = bucket_name or settings.bucket_name
        self.region = region or settings.region

        # Initialize S3 client only when using S3 backend
        if self.storage_backend == "s3":
            self.s3 = boto3.client("s3", region_name=region)
        else:
            self.s3 = None

        # Ensure local export directory exists
        self.local_export_dir = Path(local_export_dir)
        self.local_export_dir.mkdir(parents=True, exist_ok=True)

    # -------------------------
    # Public API
    # -------------------------
    def upload_excel(
        self,
        sheets: Dict[str, pd.DataFrame],
        prefix: str = "exports",
        filename_prefix: str = "export",
    ) -> str:
        """
        Export multiple DataFrames into a single Excel file.

        :param sheets: Dictionary where:
                       - key   = Excel sheet name
                       - value = pandas DataFrame
        :param prefix: Folder path (S3 key prefix or local subfolder)
        :param filename_prefix: Prefix used when generating the filename
        :return: File path (local) or S3 object key
        """

        # Validate that at least one sheet is provided
        if not sheets:
            raise ValueError("No sheets provided")

        # Prevent exporting empty sheets
        for name, df in sheets.items():
            if df.empty:
                raise ValueError(f"Sheet '{name}' has no data")

        # Generate unique Excel filename
        filename = self._generate_filename(filename_prefix)

        # Route export based on selected storage backend
        if self.storage_backend == "s3":
            return self._upload_to_s3(sheets, prefix, filename)
        else:
            return self._save_locally(sheets, prefix, filename)

    # -------------------------
    # Internal helpers
    # -------------------------
    def _generate_filename(self, prefix: str) -> str:
        """
        Generate a unique Excel filename using timestamp and UUID.

        :param prefix: Filename prefix
        :return: Filename ending with .xlsx
        """

        unique_id = uuid.uuid4().hex
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        return f"{prefix}_{timestamp}_{unique_id}.xlsx"

    def _write_excel(self, sheets: Dict[str, pd.DataFrame]) -> BytesIO:
        """
        Write Excel file to an in-memory buffer.

        Used for S3 uploads to avoid temporary files on disk.

        :param sheets: Sheet name -> DataFrame mapping
        :return: BytesIO buffer containing Excel data
        """

        buffer = BytesIO()

        # Write each DataFrame to its own Excel sheet
        with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
            for sheet_name, df in sheets.items():
                df.to_excel(
                    writer,
                    index=False,
                    sheet_name=sheet_name[:31],  # Excel sheet name limit
                )

        buffer.seek(0)
        return buffer

    def _upload_to_s3(
        self,
        sheets: Dict[str, pd.DataFrame],
        prefix: str,
        filename: str,
    ) -> str:
        """
        Upload the Excel file to AWS S3.

        :param sheets: Sheet name -> DataFrame mapping
        :param prefix: S3 key prefix (folder)
        :param filename: Excel filename
        :return: S3 object key
        """

        file_key = f"{prefix}/{filename}"

        # Generate Excel file in memory
        buffer = self._write_excel(sheets)

        # Upload file to S3
        self.s3.put_object(
            Bucket=settings.bucket_name,
            Key=file_key,
            Body=buffer.getvalue(),
            ContentType=(
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            ),
        )

        return file_key

    def _save_locally(
        self,
        sheets: Dict[str, pd.DataFrame],
        prefix: str,
        filename: str,
    ) -> str:
        """
        Save the Excel file to the local filesystem.

        :param sheets: Sheet name -> DataFrame mapping
        :param prefix: Local subfolder
        :param filename: Excel filename
        :return: Full file path as string
        """

        # Ensure subfolder exists
        folder = self.local_export_dir / prefix
        folder.mkdir(parents=True, exist_ok=True)

        file_path = folder / filename

        # Write Excel file directly to disk
        with pd.ExcelWriter(file_path, engine="openpyxl") as writer:
            for sheet_name, df in sheets.items():
                df.to_excel(
                    writer,
                    index=False,
                    sheet_name=sheet_name[:31],
                )

        return str(file_path)

    def generate_presigned_url(
        self,
        key: str,
        expires_in: int = 3600,
    ) -> str:
        """
        Generate a download URL for the exported file.

        - For S3: returns a presigned URL
        - For local: returns a file:// URL

        :param key: S3 object key or local file path
        :param expires_in: URL expiry time in seconds (S3 only)
        :return: Download URL
        """

        if self.storage_backend == "s3":
            return self.s3.generate_presigned_url(
                ClientMethod="get_object",
                Params={"Bucket": self.bucket_name, "Key": key},
                ExpiresIn=expires_in,
            )

        # Local file fallback
        return f"file:///{Path(key).resolve()}"

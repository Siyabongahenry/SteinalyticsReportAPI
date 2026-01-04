from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import List
import pandas as pd
from io import BytesIO

from app.services.lookup_service import LookupService
from app.utils.export_utils import export_excel_and_get_url

router = APIRouter(
    prefix="/lookup",
    tags=["xlookup for multiple reports"]
)

@router.post("/")
async def lookup(
    files: List[UploadFile] = File(...),
    join_by_column: str = Form(...)
):
    """
    Upload multiple CSV or Excel files and perform a LEFT JOIN.

    Rules:
    - First uploaded file is the main table
    - All other files are LEFT JOINED
    - join_by_column must exist in all uploaded files
    - Output is exported to Excel
    """

    if len(files) < 2:
        raise HTTPException(
            status_code=400,
            detail="Upload at least two files"
        )

    dataframes = []

    for file in files:
        filename = file.filename.lower()

        try:
            content = await file.read()

            if filename.endswith(".csv"):
                df = pd.read_csv(BytesIO(content))

            elif filename.endswith((".xlsx", ".xls")):
                df = pd.read_excel(BytesIO(content))

            else:
                raise HTTPException(
                    status_code=400,
                    detail=f"Unsupported file type: {file.filename}"
                )

            if join_by_column not in df.columns:
                raise HTTPException(
                    status_code=400,
                    detail=f"Column '{join_by_column}' not found in file: {file.filename}"
                )

            dataframes.append(df)

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=f"Failed to process {file.filename}: {str(e)}"
            )

    service = LookupService(
        df_reports=dataframes,
        join_by_column=join_by_column
    )

    final_df = service.join_reports()

    download_url = export_excel_and_get_url(
        sheets={"output": final_df},
        prefix="output",
        filename_prefix="xlookup_output",
    )

    return {
        "download_url": download_url,
    }

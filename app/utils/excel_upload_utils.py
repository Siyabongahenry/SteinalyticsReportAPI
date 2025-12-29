from fastapi import UploadFile, HTTPException
import pandas as pd
from io import BytesIO
from typing import Set


async def load_excel_file(
    file: UploadFile,
    required_columns: Set[str],
) -> pd.DataFrame:
    """
    Load an uploaded Excel (.xlsx) file into a pandas DataFrame.

    Validations performed:
    - File extension must be .xlsx
    - File must be readable by pandas
    - Required columns must exist in the Excel file

    :param file: Uploaded file from FastAPI request
    :param required_columns: Set of column names that must be present
    :return: pandas DataFrame containing Excel data
    """

    # Validate file extension
    if not file.filename.lower().endswith(".xlsx"):
        raise HTTPException(
            status_code=400,
            detail="Only Excel files (.xlsx) are supported",
        )

    try:
        # Read uploaded file contents into memory
        contents = await file.read()

        # Load Excel file into DataFrame
        df = pd.read_excel(BytesIO(contents), engine="openpyxl")
    except Exception as e:
        # Catch parsing and file read errors
        raise HTTPException(status_code=400, detail=str(e))

    # Validate presence of required columns
    missing = required_columns - set(df.columns)
    if missing:
        raise HTTPException(
            status_code=400,
            detail=f"Missing required columns: {', '.join(missing)}",
        )

    return df

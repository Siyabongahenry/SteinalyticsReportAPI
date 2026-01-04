from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import List
import pandas as pd
from io import BytesIO

from app.services.lookup_service import LookupService

# Create a router with a prefix and tag
router = APIRouter(
    prefix="/lookup",
    tags=["xlookup for multiple reports"]
)

@router.post("/lookup")
def lookup(
    files: List[UploadFile] = File(...),  # Accept multiple uploaded files
    join_by_column: str = Form(...)        # Column used to join all files
):
    """
    Upload multiple CSV or Excel files and perform a LEFT JOIN.

    Rules:
    - First uploaded file is the main table
    - All other files are LEFT JOINED
    """

    # Ensure at least two files are uploaded
    if len(files) < 2:
        raise HTTPException(
            status_code=400,
            detail="Upload at least two files"
        )

    dataframes = []

    # Process each uploaded file
    for file in files:
        filename = file.filename.lower()

        try:
            # Read raw file content into memory
            content = file.file.read()

            # Read CSV files
            if filename.endswith(".csv"):
                df = pd.read_csv(BytesIO(content))

            # Read Excel files
            elif filename.endswith(".xlsx") or filename.endswith(".xls"):
                df = pd.read_excel(BytesIO(content))

            # Reject unsupported file formats
            else:
                raise HTTPException(
                    status_code=400,
                    detail=f"Unsupported file type: {file.filename}"
                )

            # Store the DataFrame
            dataframes.append(df)

        except Exception as e:
            # Handle file parsing errors
            raise HTTPException(
                status_code=400,
                detail=f"Failed to process {file.filename}: {str(e)}"
            )

    # Create lookup service instance
    service = LookupService(
        df_reports=dataframes,
        join_by_column=join_by_column
    )

    # Perform the LEFT JOIN operation
    final_df = service.join_reports()

    # Return the result as JSON
    return {
        "rows": len(final_df),                      # Total number of rows
        "columns": list(final_df.columns),          # Column names
        "data": final_df.to_dict(orient="records")  # Table data
    }

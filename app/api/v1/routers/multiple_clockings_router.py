from fastapi import APIRouter,UploadFile,File
from app.utils.excel_upload_utils import load_excel_file
from app.utils.export_utils import export_excel_and_get_url
from pathlib import Path
from app.services.multiple_clockings_service import MultipleClockigsService

router = APIRouter(prefix="/multiple-clockings",tags=["multiple clockings report"])

@router.post("/multiple-clockings")
async def multiple_clockings(file:UploadFile):
    """
    Validate VIP codes from an uploaded Excel file and export incorrect entries.

    Workflow:
    1. Load Excel file into a pandas DataFrame
    2. Remove reversed/cancelled entries
    3. Identify incorrect VIP codes using business rules
    4. Export incorrect rows to Excel and return a download URL
    """

    # Load and validate the uploaded Excel file
    # Ensures required columns exist before processing
    df = await load_excel_file(
        file,
        required_columns={"Clock No.","Date"},
    )

    multiple_clockings_service = MultipleClockigsService(df)

    multiple_clockings = multiple_clockings_service.getMultipleClockings()

    # Return early if no issues are found
    if multiple_clockings:
        return {
            "message": "Multiple clockings not found",
            "incorrect_rows": 0,
        }

    # Export validation results to Excel and generate download URL
    download_url = export_excel_and_get_url(
        sheets={
            "Multiple clockings": multiple_clockings,
        },
        prefix="multiple-clockings",
        filename_prefix="multiple_clockings",
    )

    # Return summary and download link
    return {
        "multiple_clockings_count": len(multiple_clockings),
        "download_url": download_url,
    }



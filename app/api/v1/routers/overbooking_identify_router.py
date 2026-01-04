from fastapi import APIRouter, UploadFile, File
from app.services.overbooking_service import OverbookingService
from app.utils.reversed_entries_utils import remove_reversed_entries
from app.utils.excel_upload_utils import load_excel_file
from app.utils.export_utils import export_excel_and_get_url

# Router responsible for detecting duplicate and overbooking issues
router = APIRouter(prefix="/overbooking", tags=["Overbooking Validation"])


@router.post("/overbooking")
async def overbooking(file: UploadFile = File(...)):
    """
    Validate duplicate and overbooked time entries from an uploaded Excel file.

    Workflow:
    1. Load Excel file into a pandas DataFrame
    2. Remove reversed/cancelled entries
    3. Detect duplicated overtime entries
    4. Detect overbooked normal daily hours
    5. Export incorrect rows to Excel and return a download URL
    """

    # Load and validate the uploaded Excel file
    # Ensures required columns exist before processing
    df = await load_excel_file(
        file,
        required_columns={"Entry No.","Resource     no.", "VIP Code","Hours worked","Applies-To Entry"},
    )

    # Remove reversed or invalid accounting entries
    clean_df = remove_reversed_entries(df)

    # Initialize overbooking validation service
    overbooking = OverbookingService(clean_df)

    # Find duplicated overtime entries
    duplicated = overbooking.find_duplicates_overtime()

    # Find overbooked normal daily entries
    overbooked = overbooking.find_overbooked_normal_daily()

    # Return early if no issues are found
    if duplicated.empty and overbooked.empty:
        return {
            "message": "No duplicate or overbooked entries found",
            "incorrect_rows": 0,
        }

    # Export validation results to Excel and generate download URL
    download_url = export_excel_and_get_url(
        sheets={
            "Duplicated Overtime": duplicated,
            "Overbooked Normal Daily": overbooked,
        },
        prefix="duplicate-validation",
        filename_prefix="duplicate_overbooking",
    )

    # Return summary and download link
    return {
        "incorrect_rows": len(duplicated) + len(overbooked),
        "download_url": download_url,
    }

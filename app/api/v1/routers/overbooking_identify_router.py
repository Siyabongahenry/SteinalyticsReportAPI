from fastapi import APIRouter, Depends
from app.services.overbooking_service import OverbookingService
from app.utils.reversed_entries_utils import remove_reversed_entries
from app.utils.excel_upload_utils import load_excel_file
from app.utils.export_utils import export_excel_and_get_url
from app.dependencies.file_upload_validator import FileUploadValidator

router = APIRouter(
    prefix="/overbooking",
    tags=["Overbooking Validation"]
)

@router.post("")
async def overbooking(contents: bytes = Depends(FileUploadValidator())):
    """
    Validate duplicate and overbooked time entries from an uploaded Excel file.

    Workflow:
    1. Load Excel file into a pandas DataFrame
    2. Remove reversed/cancelled entries
    3. Detect duplicated overtime entries
    4. Detect overbooked normal daily hours
    5. Export incorrect rows to Excel and return a download URL
    """

    df = await load_excel_file(
        contents,
        required_columns={
            "Entry No.",
            "Resource no.",
            "VIP Code",
            "Hours worked",
            "Applies-To Entry",
        },
    )

    clean_df = remove_reversed_entries(df)

    service = OverbookingService(clean_df)

    duplicated = service.find_duplicates_overtime()
    overbooked = service.find_overbooked_normal_daily()

    if duplicated.empty and overbooked.empty:
        return {
            "message": "No duplicate or overbooked entries found",
            "incorrect_rows": 0,
        }

    download_url = export_excel_and_get_url(
        sheets={
            "Duplicated Overtime": duplicated,
            "Overbooked Normal Daily": overbooked,
        },
        prefix="duplicate-validation",
        filename_prefix="duplicate_overbooking",
    )

    return {
        "incorrect_rows": len(duplicated) + len(overbooked),
        "download_url": download_url,
    }

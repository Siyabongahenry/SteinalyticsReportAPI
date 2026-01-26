from fastapi import APIRouter, Depends
from app.utils.excel_upload_utils import load_excel_file
from app.utils.export_utils import export_excel_and_get_url
from app.services.multiple_clockings_service import MultipleClockingsService 
from app.dependencies.file_upload_validator import FileUploadValidator
from app.dependencies.roles import require_role

router = APIRouter(
    prefix="/multiple-clockings",
    tags=["multiple clockings report"]
)

@router.post("")
async def multiple_clockings(user = Depends(require_role('site-admin')),contents: bytes = Depends(FileUploadValidator())):
    """
    Identify multiple clockings from an uploaded Excel file.

    Workflow:
    1. Load Excel file into a pandas DataFrame
    2. Validate required columns
    3. Identify multiple clockings
    4. Export results to Excel and return a download URL
    """

    df = await load_excel_file(
        contents,
        required_columns={"Clock No.", "Date"},
    )

    service = MultipleClockingsService(df)
    multiple_clockings = service.getMultipleClockings()

    # No issues found
    if multiple_clockings.empty:
        return {
            "message": "Multiple clockings not found",
            "multiple_clockings_count": 0,
        }
    
    user_id = user.get("sub")

    download_url = export_excel_and_get_url(
        sheets={"Multiple clockings": multiple_clockings},
        prefix="multiple-clockings",
        filename_prefix="multiple_clockings",
        user_id=user_id
    )

    return {
        "multiple_clockings_count": len(multiple_clockings),
        "download_url": download_url,
    }

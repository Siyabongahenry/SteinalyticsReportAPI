from fastapi import APIRouter,UploadFile,File
from app.utils.excel_upload_utils import load_excel_file
from app.utils.export_utils import export_excel_and_get_url
from pathlib import Path

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
        required_columns={"Entry No.","Resource     no.", "VIP Code","Hours worked","Applies-To Entry"},
    )

from fastapi import APIRouter, Depends
from app.services.incorrect_vip_service import IncorrectVIPService
from app.utils.reversed_entries_utils import remove_reversed_entries
from app.utils.excel_upload_utils import load_excel_file
from app.utils.export_utils import export_excel_and_get_url
from app.dependencies.file_upload_validator import FileUploadValidator
from pathlib import Path

# Create a router dedicated to VIP-related validation endpoints
router = APIRouter(prefix="/vip-validation", tags=["VIP Validation"])

# Resolve the base directory of the project
# parents[3] is used to navigate from this file to the project root
BASE_DIR = Path(__file__).resolve().parents[3]

# Path to VIP code configuration file
CONFIG_PATH = BASE_DIR / "core" / "vipcodes.json"


@router.post("")
async def validate_and_export(contents: bytes = Depends(FileUploadValidator())):
    """
    Validate VIP codes from an uploaded Excel file and export incorrect entries.

    Workflow:
    1. Load Excel file into a pandas DataFrame
    2. Remove reversed/cancelled entries
    3. Identify incorrect VIP codes using business rules
    4. Export incorrect rows to Excel and return a download URL
    """

    print("VIP Router Reached")

    # Load and validate the uploaded Excel file
    # Ensures required columns exist before processing
    df = await load_excel_file(
        contents,
        required_columns={"Entry No.","Resource no.", "VIP Code","Hours worked","Applies-To Entry"},
    )
    print("File converted to a df")
    # Remove reversed or invalid accounting entries
    clean_df = remove_reversed_entries(df)

    # Run VIP validation logic using external configuration
    incorrect_df = IncorrectVIPService(
        clean_df,
        CONFIG_PATH,
    ).find_incorrect_vip()

    # If no incorrect VIP codes are found, return early
    if incorrect_df.empty:
        return {
            "message": "No incorrect VIP codes found",
            "incorrect_rows": 0,
        }

    print("Creating url")
    # Export incorrect VIP rows to Excel and generate a download URL
    download_url = export_excel_and_get_url(
        sheets={"Incorrect VIP Codes": incorrect_df},
        prefix="vip-validation",
        filename_prefix="incorrect_vip",
    )
    print("Url created")
    # Return summary and download link
    return {
        "incorrect_rows": len(incorrect_df),
        "download_url": download_url,
    }

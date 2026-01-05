from fastapi import APIRouter, UploadFile, File
from app.utils.excel_upload_utils import load_excel_file
from app.utils.export_utils import export_excel_and_get_url
from app.utils.reversed_entries_utils import remove_reversed_entries
from app.services.exemption_service import ExemptionService

router = APIRouter(
    prefix="/exemption",
    tags=["Exemption report"]
)

@router.post("/")
async def exemption_report(
    file: UploadFile = File(...),
    exemption_type: str = ""
):
    # Load and validate the uploaded Excel file
    df = await load_excel_file(
        file,
        required_columns={
            "Entry No.",
            "Resource no.",
            "VIP Code",
            "Hours worked",
            "Applies-To Entry",
        },
    )

    # Remove reversed or invalid accounting entries
    clean_df = remove_reversed_entries(df, "week")

    exemption_service = ExemptionService(clean_df, exemption_type)
    exemption_df = exemption_service.get_exemption()

    if exemption_df.empty:
        return {
            "message": "No exemption exceeded"
        }

    # Export exemption rows to Excel and generate a download URL
    download_url = export_excel_and_get_url(
        sheets={"Exemption": exemption_df},
        prefix="exemption-report",
        filename_prefix="exemption_report",
    )

    return {
        "message": "Exemption report generated successfully",
        "download_url": download_url
    }

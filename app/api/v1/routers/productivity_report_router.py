from fastapi import APIRouter, Depends
from app.dependencies.file_upload_validator import FileUploadValidator

from app.utils.reversed_entries_utils import remove_reversed_entries
from app.utils.excel_upload_utils import load_excel_file
from app.utils.export_utils import export_excel_and_get_url
from app.dependencies.roles import require_role


from app.services.productivity_report_service import ProductivityReportService

router = APIRouter(prefix="productivity-report",tags=["Productivity report"])

@router.post("")
async def productivity_report(user = Depends(require_role("site-admin")),contents: bytes = Depends(FileUploadValidator())):
    
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

    service = ProductivityReportService(clean_df)

    hours_worked_df = service.df_hours_worked()
    productive_posted = service.productive_hours_posted(0)
    allowance_posted_df = service.allowance_posted()
    summary_df = service.get_summary()

    user_id = user.get('sub')

    urls = export_excel_and_get_url(
        sheets={
            "Hours worked": hours_worked_df,
            "Productive posted": productive_posted,
            "Allowance posted":allowance_posted_df,
            "summary": summary_df
        },
        prefix="productivity reporr",
        filename_prefix="productivity report",
        user_id = user_id
    )

    return{
        "summary":summary_df,
        "download_url":urls["download_url"]
    }



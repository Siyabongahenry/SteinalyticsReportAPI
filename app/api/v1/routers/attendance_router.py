from fastapi import APIRouter,Depends
from app.services.attendence_service import AttendanceService
from app.dependencies.file_upload_validator import FileUploadValidator
from app.utils.excel_upload_utils import load_excel_file
from app.utils.export_utils import export_excel_and_get_url

router = APIRouter(prefix = "attendance",tags="Employees attendance")

@router.post("/list")
async def attendence_list(contents: bytes = Depends(FileUploadValidator())):

    df = await load_excel_file(
       contents,
        required_columns={
            "Clock No.",
            "Date",
            "WTT"
        },
     )
    
    attendence_service = AttendanceService(df)

    attendence_list = attendence_service.get_employees_list()

    download_url = export_excel_and_get_url(
        sheets={
            "Attendence_list":  attendence_list
        },
        prefix="Employees attence list",
        filename_prefix="attendance_list",
     )


    return {
        "download_url":download_url
    }

@router.post("/site-summary")
async def site_summary(contents: bytes = Depends(FileUploadValidator())):

    df = await load_excel_file(
       contents,
        required_columns={
            "Clock No.",
            "Date",
            "WTT"
        },
     )
    
    attendence_service = AttendanceService(df)

    attendence_list = attendence_service.get_summary_by_site()

    download_url = export_excel_and_get_url(
        sheets={
            "Attendence_summary":  attendence_list
        },
        prefix="Site attendence summary",
        filename_prefix="site_attence",
     )


    return {
        "download_url":download_url
    }
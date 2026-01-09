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

@router.post("/employee-attendance-summary")
async def employee_attendance_summary(contents: bytes = Depends(FileUploadValidator())):
    """
    Returns weekly and monthly attendance per employee.
    Attendance rules:
    - Clock No. uniquely identifies an employee
    - One attendance per employee per day
    - Multiple scans per day are ignored
    """

    # Load Excel file and validate required columns
    df = await load_excel_file(
        contents,
        required_columns={"Clock No.", "Date", "WTT"},
    )

    # Initialize the service with the uploaded DataFrame
    attendance_service = AttendanceService(df)

    # Get weekly and monthly attendance
    weekly_attendance = attendance_service.get_attendance_by_employee_week()
    monthly_attendance = attendance_service.get_attendance_by_employee_month()

    # Export both summaries to Excel
    download_url = export_excel_and_get_url(
        sheets={
            "Weekly_attendance": weekly_attendance,
            "Monthly_attendance": monthly_attendance,
        },
        prefix="Employee_attendance_summary",
        filename_prefix="employee_attendance",
    )

    return {
        "download_url": download_url
    }

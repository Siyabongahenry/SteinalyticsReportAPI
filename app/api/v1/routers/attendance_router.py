from fastapi import APIRouter, Depends
from app.services.attendence_service import AttendanceService
from app.dependencies.file_upload_validator import FileUploadValidator
from app.utils.excel_upload_utils import load_excel_file
from app.utils.export_utils import export_excel_and_get_url
from app.dependencies.roles import require_role

# Create a FastAPI router for attendance-related endpoints
router = APIRouter(prefix="/attendance", tags=["Employees attendance"])

@router.post("/list")
async def attendence_list(user = Depends(require_role("site-admin")),contents: bytes = Depends(FileUploadValidator())):
    """
    Endpoint: /attendance/list
    Returns a list of unique employee attendances.
    
    Rules:
    - Clock No. uniquely identifies an employee
    - WTT is the site
    - One attendance per employee per site per day
    - Multiple scans per day are ignored
    """

    # Load the uploaded Excel file and validate required columns
    df = await load_excel_file(
        contents,
        required_columns={"Clock No.", "Date", "WTT"},
    )

    # Initialize the attendance service with the DataFrame
    attendence_service = AttendanceService(df)

    # Get the unique attendance list
    attendence_list = attendence_service.get_employees_list()

    user_id = user.get("sub")


    # Export the attendance list to Excel and get a download URL
    download_url = export_excel_and_get_url(
        sheets={"Attendence_list": attendence_list},
        prefix="Employees attence list",
        filename_prefix="attendance_list",
        user_id = user_id
    )

    # Return the download link to the client
    return {"download_url": download_url}

@router.post("/site-summary")
async def site_summary(contents: bytes = Depends(FileUploadValidator())):
    """
    Endpoint: /attendance/site-summary
    Returns attendance summary per site per day.
    
    Rules:
    - Counts unique employees per site per day
    - Multiple scans per employee per day are ignored
    """

    # Load the uploaded Excel file and validate required columns
    df = await load_excel_file(
        contents,
        required_columns={"Clock No.", "Date", "WTT"},
    )

    # Initialize the attendance service with the DataFrame
    attendence_service = AttendanceService(df)

    # Get attendance summary per site per day
    attendence_list = attendence_service.get_summary_by_site()

    # Export the summary to Excel and get a download URL
    download_url = export_excel_and_get_url(
        sheets={"Attendence_summary": attendence_list},
        prefix="Site attendence summary",
        filename_prefix="site_attence",
    )

    # Return the download link to the client
    return {"download_url": download_url}

@router.post("/employee-attendance-summary")
async def employee_attendance_summary(contents: bytes = Depends(FileUploadValidator())):
    """
    Endpoint: /attendance/employee-attendance-summary
    Returns weekly and monthly attendance per employee.
    
    Rules:
    - Clock No. uniquely identifies an employee
    - One attendance per employee per day (multiple scans ignored)
    - Weekly attendance: number of days present in each week
    - Monthly attendance: number of days present in each month
    """

    # Load the uploaded Excel file and validate required columns
    df = await load_excel_file(
        contents,
        required_columns={"Clock No.", "Date", "WTT"},
    )

    # Initialize the attendance service with the DataFrame
    attendance_service = AttendanceService(df)

    # Compute weekly attendance per employee
    weekly_attendance = attendance_service.get_attendance_by_employee_week()

    # Compute monthly attendance per employee
    monthly_attendance = attendance_service.get_attendance_by_employee_month()

    # Export both weekly and monthly summaries to Excel and get download URL
    download_url = export_excel_and_get_url(
        sheets={
            "Weekly_attendance": weekly_attendance,
            "Monthly_attendance": monthly_attendance,
        },
        prefix="Employee_attendance_summary",
        filename_prefix="employee_attendance",
    )

    # Return the download link to the client
    return {"download_url": download_url}

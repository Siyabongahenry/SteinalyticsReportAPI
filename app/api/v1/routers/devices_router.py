from fastapi import APIRouter,UploadFile,File
from app.utils.excel_upload_utils import load_excel_file
from app.utils.export_utils import export_excel_and_get_url
from app.services.device_service import DeviceService
router = APIRouter(prefix="devices",tags=["Devices count"])

@router.post("/")
async def devices_count(file:UploadFile = File(...)):
     df = await load_excel_file(
        file,
        required_columns={
            "MeterId",
            "Date",
        },
     )
     
     device_service = DeviceService(df)

     download_url = export_excel_and_get_url(
        sheets={
            "Device report": device_service,
        },
        prefix="duplicate-validation",
        filename_prefix="duplicate_overbooking",
     )

     return {
        "download_url": download_url,
        "incorrect_rows": DeviceService
     }
     





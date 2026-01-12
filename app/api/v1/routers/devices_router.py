from fastapi import APIRouter, Depends
from app.utils.excel_upload_utils import load_excel_file
from app.utils.export_utils import export_excel_and_get_url
from app.services.device_service import DeviceService
from app.dependencies.file_upload_validator import FileUploadValidator



router = APIRouter(prefix="/device-clockings",tags=["Devices count"])


@router.post("")
async def devices_count(contents: bytes = Depends(FileUploadValidator())):
     df = await load_excel_file(
       contents,
        required_columns={
            "MeterId",
            "Date",
        },
     )
     
     device_service = DeviceService(df)

     clockings_count = device_service.clockings_count()

     download_url = export_excel_and_get_url(
        sheets={
            "Device report":  clockings_count,
        },
        prefix="clockings count per machine",
        filename_prefix="clockings_count",
     )

     return {
        "download_url": download_url,
        "data": clockings_count
     }
     





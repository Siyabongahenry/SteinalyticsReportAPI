from fastapi import APIRouter, Depends
from typing import List
import pandas as pd
from io import BytesIO

from app.services.lookup_service import LookupService
from app.utils.export_utils import export_excel_and_get_url

from app.dependencies.multiple_file_validator import MultiFileValidator

router = APIRouter(
    prefix="/lookup",
    tags=["xlookup for multiple reports"]
)

@router.post("")
async def lookup(dataframes: List[pd.DataFrame] = Depends(MultiFileValidator())):
    """
    Upload multiple CSV or Excel files and perform a LEFT JOIN.
    """
    service = LookupService(
        df_reports=dataframes,
        join_by_column=dataframes[0].columns[0]  # or pass explicitly if needed
    )

    final_df = service.join_reports()

    download_url = export_excel_and_get_url(
        sheets={"output": final_df},
        prefix="output",
        filename_prefix="xlookup_output",
    )

    return {"download_url": download_url}

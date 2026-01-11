from fastapi import UploadFile, HTTPException
import pandas as pd
from io import BytesIO
from typing import Set


async def load_excel_file(contents: bytes, required_columns: Set[str]) -> pd.DataFrame:
    try:
        
        df = pd.read_excel(BytesIO(contents), engine="openpyxl")

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    
    missing = required_columns - set(df.columns)
    if missing:
        raise HTTPException(status_code=400, detail=f"Missing required columns: {', '.join(missing)}")

    return df

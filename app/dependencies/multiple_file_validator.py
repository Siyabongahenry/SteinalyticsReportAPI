from fastapi import UploadFile, File, Form, HTTPException
from typing import List, Set
import pandas as pd
from io import BytesIO

class MultiFileValidator:
    def __init__(self, max_size: int = 10 * 1024 * 1024, allowed_types: Set[str] = None):
        self.max_size = max_size
        self.allowed_types = allowed_types or {
            "text/csv",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        }

    async def __call__(
        self,
        files: List[UploadFile] = File(...),
        join_by_column: str = Form(...),
    ) -> List[pd.DataFrame]:
        if len(files) < 2:
            raise HTTPException(status_code=400, detail="Upload at least two files")

        dataframes = []
        for file in files:
            filename = file.filename.lower()
            contents = await file.read()

            if len(contents) > self.max_size:
                raise HTTPException(
                    status_code=400,
                    detail=f"File {file.filename} too large. Max size is {self.max_size / (1024*1024)} MB.",
                )

            try:
                if filename.endswith(".csv"):
                    df = pd.read_csv(BytesIO(contents))
                elif filename.endswith((".xlsx", ".xls")):
                    df = pd.read_excel(BytesIO(contents))
                else:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Unsupported file type: {file.filename}",
                    )
            except Exception as e:
                raise HTTPException(
                    status_code=400,
                    detail=f"Failed to process {file.filename}: {str(e)}",
                )

            if join_by_column not in df.columns:
                raise HTTPException(
                    status_code=400,
                    detail=f"Column '{join_by_column}' not found in file: {file.filename}",
                )

            dataframes.append(df)

        return dataframes

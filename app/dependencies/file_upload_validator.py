from fastapi import UploadFile,File, HTTPException
from typing import List

class FileUploadValidator:
    def __init__(self, max_size: int = 10 * 1024 * 1024, allowed_types: List[str] = None):
        if allowed_types is None:
            allowed_types = [
                "text/csv",
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            ]
        self.max_size = max_size
        self.allowed_types = allowed_types

    async def __call__(self, file: UploadFile= File(...)):

        # ✅ Validate content type
        if file.content_type not in self.allowed_types:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file type: {file.content_type}. Only CSV or Excel allowed."
            )

        # ✅ Validate file size
        contents = await file.read()
        if len(contents) > self.max_size:
            raise HTTPException(
                status_code=400,
                detail=f"File too large. Max size is {self.max_size / (1024*1024)} MB."
            )
    

        return contents

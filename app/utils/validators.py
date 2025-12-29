from fastapi import UploadFile, HTTPException

def validate_excel(file: UploadFile):
    if not file.filename.endswith((".xlsx", ".xls")):
        raise HTTPException(status_code=400, detail="Invalid Excel file")

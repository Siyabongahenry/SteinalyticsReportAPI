from fastapi import APIRouter, HTTPException, Depends
from app.services.book_identifier_service import BookIdentifierService
from app.dependencies.roles import require_role
from app.dependencies.image_upload_validator import ImageUploadValidator

router = APIRouter(
    prefix="/books-identifier",
    tags=["Book Identifier"],
    dependencies=[Depends(require_role("site-admin"))]
)

service = BookIdentifierService()

@router.post("/identify")
async def identify_book(file=Depends(ImageUploadValidator)):
    """
    Endpoint: POST /books/identify
    Accepts an uploaded image file (book cover).
    Runs OCR + metadata lookup pipeline.
    Returns book title, authors, language, categories.
    """
    try:
        image_bytes = await file.read()
        result = service.identify_book(image_bytes)

        if not result.get("title"):
            return {"message": "No matching book found", "matched_text": result["matched_text"]}

        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/describe")
async def describe_book(title: str = None, author: str = None, isbn: str = None):
    try:
       
        result = service.describe_book(title = title,author = author, isbn = isbn)

        if not result.get("title"):
            return {"message": "No matching book found", "matched_text": result["matched_text"]}

        return {"description":result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

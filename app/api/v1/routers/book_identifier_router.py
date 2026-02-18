from fastapi import APIRouter, HTTPException, Depends
from app.services.book_identifier_service import BookIdentifierService
from app.dependencies.roles import require_role
from app.dependencies.image_upload_validator import ImageUploadValidator
from app.core.logger import logger
from pydantic import BaseModel

router = APIRouter(
    prefix="/books-identifier",
    tags=["Book Identifier"]
)

service = BookIdentifierService()

class BookRequest(BaseModel):
     title: str = None
     author: str = None
     isbn: str = None


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
async def describe_book(book: BookRequest):
    #try:

        logger.info("Describe route reached") 
        logger.info(f"Received parameters - Title: {book.title}, Author: {book.author}, ISBN: {book.isbn}")

        logger.info("describe route reached")

        result = service.describe_book(title = book.title,author = book.author, isbn = book.isbn)

        logger.info("Results obtained")
        

        if not result.get("title"):
            return {"message": "No matching book found", "matched_text": result["matched_text"]}

        return {"description":result}
    #except Exception as e:
        #raise HTTPException(status_code=500, detail=str(e))

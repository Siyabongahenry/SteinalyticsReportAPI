from fastapi import APIRouter, UploadFile, File, HTTPException,Depends
from app.services.book_identifier_service import BookIdentifierService
from app.dependencies.roles import require_role

# Define router with prefix and tags for documentation
router = APIRouter(
    prefix="/books", 
    tags=["Book Identifier"],
    dependencies=[Depends(require_role("site-admin"))]
)

# Initialize service
service = BookIdentifierService()

@router.post("/identify")
async def identify_book(file: UploadFile = File(...)):
    """
    Endpoint: POST /books/identify
    Accepts an uploaded image file (book cover).
    Runs OCR + metadata lookup pipeline.
    Returns book title, authors, language, categories.
    """
    try:
        # Read uploaded file into memory
        image_bytes = await file.read()

        # Call service to identify book
        result = service.identify_book(image_bytes)

        # If no match found, return message
        if not result.get("title"):
            return {"message": "No matching book found", "matched_text": result["matched_text"]}

        # Return structured metadata
        return result
    except Exception as e:
        # Catch unexpected errors and return HTTP 500
        raise HTTPException(status_code=500, detail=str(e))

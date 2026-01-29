from fastapi import APIRouter, Depends, Form
from datetime import datetime, timezone
from app.dependencies.image_upload_validator import ImageUploadValidator
from app.services.book_service import BookService
from app.dependencies.roles import require_role

router = APIRouter(prefix="/books", tags=["Books"])

# --------------------
# Donate Book
# --------------------
@router.post("/donate")
async def donate_book(
    user=Depends(require_role("site-admin")),
    file=Depends(ImageUploadValidator),
    title: str = Form(...),
    author: str = Form(...),
    language: str = Form(...),
    category: str = Form(...),
    isbn: str = Form(...),
):
    user_id = user.get("sub")
    created_at = datetime.now(timezone.utc).isoformat()

    service = BookService()
    book = await service.add_book(
        title=title,
        author=author,
        language=language,
        category=category,
        isbn=isbn,
        file=file,
        user_id=user_id,
        created_at=created_at,
    )
    return {"message": "Book donated successfully", "book": book}


# --------------------
# Borrow Book
# --------------------
@router.post("/{book_id}/borrow")
async def borrow_book(book_id: str, user=Depends(require_role("user"))):
    user_id = user.get("sub")
    borrowed_at = datetime.now(timezone.utc).isoformat()
    return_date = datetime.now(timezone.utc).replace(
        hour=0, minute=0, second=0, microsecond=0
    ).isoformat()

    service = BookService()
    updated = await service.borrow_book(
        book_id=book_id,
        user_id=user_id,
        borrowed_at=borrowed_at,
        return_date=return_date,
    )
    return {"message": "Book borrowed", "book": updated}


# --------------------
# Return Book
# --------------------
@router.post("/{book_id}/return")
async def return_book(book_id: str, user=Depends(require_role("user"))):
    user_id = user.get("sub")
    returned_at = datetime.now(timezone.utc).isoformat()

    service = BookService()
    updated = await service.return_book(
        book_id=book_id,
        user_id=user_id,
        returned_at=returned_at,
    )
    return {"message": "Book returned", "book": updated}


# --------------------
# Update Book (admin use)
# --------------------
@router.put("/{book_id}")
async def update_book(
    book_id: str,
    status: str = Form(None),
    borrowed_at: str = Form(None),
    return_date: str = Form(None),
    waiting_list: str = Form(None),
):
    service = BookService()
    updated = await service.update_book(
        book_id=book_id,
        status=status,
        borrowed_at=borrowed_at,
        return_date=return_date,
        waiting_list=waiting_list.split(",") if waiting_list else None,
    )
    return {"message": "Book updated", "book": updated}


# --------------------
# Delete Book
# --------------------
@router.delete("/{book_id}")
async def delete_book(book_id: str):
    service = BookService()
    await service.delete_book(book_id)
    return {"message": f"Book {book_id} deleted"}


# --------------------
# Get Book
# --------------------
@router.get("/{book_id}")
async def get_book(book_id: str):
    service = BookService()
    book = await service.get_book(book_id)
    return {"book": book}


# --------------------
# List Books
# --------------------
@router.get("/")
async def list_books():
    service = BookService()
    books = await service.list_books()
    return {"books": books}

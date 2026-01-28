import uuid
from datetime import datetime
from fastapi import APIRouter, Depends, UploadFile, File, Form
from app.dependencies.roles import require_role
from app.services.book_service import BookService

router = APIRouter(prefix="/books", tags=["Books"])

@router.post("/donate")
async def donate_book(
    user=Depends(require_role("user")),
    title: str = Form(...),
    author: str = Form(...),
    language: str = Form(...),
    category: str = Form(...),
    isbn: str = Form(...),
    file: UploadFile = File(...),
):
    user_id = user.get("sub")
    created_at = datetime.utcnow().isoformat()
    file_ext = file.filename.split(".")[-1]
    unique_filename = f"{uuid.uuid4()}.{file_ext}"

    service = BookService()
    book = await service.add_book(
        title=title,
        author=author,
        language=language,
        category=category,
        isbn=isbn,
        file=file,
        filename=unique_filename,
        user_id=user_id,
        created_at=created_at,
    )
    return {"message": "Book donated successfully", "book": book}


@router.put("/{book_id}")
async def update_book(
    book_id: str,
    status: str = Form(None),
    borrowed_at: str = Form(None),
    return_date: str = Form(None),
    waiting_list: str = Form(None),  # comma-separated user IDs
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


@router.delete("/{book_id}")
async def delete_book(book_id: str):
    service = BookService()
    await service.delete_book(book_id)
    return {"message": f"Book {book_id} deleted"}


@router.get("/{book_id}")
async def get_book(book_id: str):
    service = BookService()
    book = await service.get_book(book_id)
    return {"book": book}


@router.get("/")
async def list_books():
    service = BookService()
    books = await service.list_books()
    return {"books": books}

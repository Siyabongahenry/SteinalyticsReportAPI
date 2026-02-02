import io
import uuid
import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime, timezone

from app.services.book_service import BookService

class MockUploadFile:
    def __init__(self, filename="test.pdf", content=b"dummy content"):
        self.filename = filename
        self.file = io.BytesIO(content)

@pytest.fixture
def mock_table():
    table = MagicMock()
    table.put_item.return_value = {}
    table.get_item.return_value = {
        "Item": {"id": "book-id", "title": "Test Book"}
    }
    table.scan.return_value = {
        "Items": [{"id": "book-id", "title": "Test Book"}]
    }
    table.update_item.return_value = {
        "Attributes": {"id": "book-id", "status": "borrowed"}
    }
    return table

@pytest.fixture
def mock_s3():
    s3 = MagicMock()
    s3.upload_fileobj.return_value = None
    return s3


@pytest.fixture
def book_service(mock_table, mock_s3):
    with patch("app.services.book_service.get_table", return_value=mock_table), \
         patch("boto3.client", return_value=mock_s3):
        service = BookService(table_name="books")
        service.bucket = "test-bucket"
        return service
@pytest.mark.asyncio
async def test_add_book(book_service, mock_table):
    file = MockUploadFile()

    book = await book_service.add_book(
        title="Clean Code",
        author="Robert C. Martin",
        language="EN",
        category="Programming",
        isbn="1234567890",
        file=file,
        user_id="user-1",
    )

    assert book["title"] == "Clean Code"
    assert book["status"] == "available"
    assert book["file_url"].startswith("https://test-bucket.s3.amazonaws.com/")
    mock_table.put_item.assert_called_once()

@pytest.mark.asyncio
async def test_get_book(book_service):
    book = await book_service.get_book("book-id")

    assert book["id"] == "book-id"
@pytest.mark.asyncio
async def test_list_books(book_service):
    books = await book_service.list_books()

    assert len(books) == 1
    assert books[0]["title"] == "Test Book"

@pytest.mark.asyncio
async def test_borrow_book(book_service):
    borrowed_at = datetime.now(timezone.utc).isoformat()
    return_date = datetime.now(timezone.utc).isoformat()

    book = await book_service.borrow_book(
        book_id="book-id",
        user_id="user-1",
        borrowed_at=borrowed_at,
        return_date=return_date,
    )

    assert book["status"] == "borrowed"

@pytest.mark.asyncio
async def test_return_book(book_service):
    book = await book_service.return_book(
        book_id="book-id",
        user_id="user-1",
        returned_at=datetime.now(timezone.utc).isoformat(),
    )

    assert book["status"] == "borrowed"  # based on mocked response

@pytest.mark.asyncio
async def test_delete_book(book_service, mock_table):
    await book_service.delete_book("book-id")

    mock_table.delete_item.assert_called_once_with(Key={"id": "book-id"})

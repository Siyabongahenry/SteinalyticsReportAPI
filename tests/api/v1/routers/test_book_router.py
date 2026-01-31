import io
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch

from app.api.books import router
from app.dependencies.roles import require_role
from app.dependencies.image_upload_validator import ImageUploadValidator

@pytest.fixture
def app():
    app = FastAPI()
    app.include_router(router)
    return app


@pytest.fixture
def client(app):
    return TestClient(app)

@pytest.fixture(autouse=True)
def override_roles(app):
    def fake_role(role: str):
        return {"sub": "test-user"}

    app.dependency_overrides[require_role] = fake_role
    yield
    app.dependency_overrides.clear()

class MockUploadFile:
    filename = "book.jpg"

    async def read(self):
        return b"fake-image-bytes"


@pytest.fixture(autouse=True)
def override_image_validator(app):
    app.dependency_overrides[ImageUploadValidator] = lambda: MockUploadFile()
    yield
    app.dependency_overrides.pop(ImageUploadValidator, None)


@pytest.fixture
def mock_book_service():
    service = AsyncMock()
    service.add_book.return_value = {"id": "1", "title": "Clean Code"}
    service.borrow_book.return_value = {"id": "1", "status": "borrowed"}
    service.return_book.return_value = {"id": "1", "status": "available"}
    service.update_book.return_value = {"id": "1", "status": "updated"}
    service.get_book.return_value = {"id": "1", "title": "Clean Code"}
    service.list_books.return_value = [{"id": "1", "title": "Clean Code"}]
    return service

def test_donate_book(client, mock_book_service):
    with patch(
        "app.api.books.BookService",
        return_value=mock_book_service
    ):
        response = client.post(
            "/books/donate",
            data={
                "title": "Clean Code",
                "author": "Robert Martin",
                "language": "EN",
                "category": "Programming",
                "isbn": "1234567890",
            },
            files={"file": ("book.jpg", b"img", "image/jpeg")},
        )

    assert response.status_code == 200
    assert response.json()["message"] == "Book donated successfully"

def test_borrow_book(client, mock_book_service):
    with patch("app.api.books.BookService", return_value=mock_book_service):
        response = client.post("/books/1/borrow")

    assert response.status_code == 200
    assert response.json()["book"]["status"] == "borrowed"


def test_update_book(client, mock_book_service):
    with patch("app.api.books.BookService", return_value=mock_book_service):
        response = client.put(
            "/books/1",
            data={
                "status": "borrowed",
                "waiting_list": "u1,u2"
            }
        )

    assert response.status_code == 200
    assert response.json()["message"] == "Book updated"

def test_delete_book(client, mock_book_service):
    with patch("app.api.books.BookService", return_value=mock_book_service):
        response = client.delete("/books/1")

    assert response.status_code == 200
    assert "deleted" in response.json()["message"]

def test_list_books(client, mock_book_service):
    with patch("app.api.books.BookService", return_value=mock_book_service):
        response = client.get("/books/")

    assert response.status_code == 200
    assert len(response.json()["books"]) == 1

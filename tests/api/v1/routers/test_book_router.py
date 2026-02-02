import pytest
from fastapi import FastAPI, HTTPException, status
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch

from app.api.books import router
from app.dependencies.roles import require_role
from app.dependencies.image_upload_validator import ImageUploadValidator


# ======================================================
# APP & CLIENT
# ======================================================

@pytest.fixture
def app():
    app = FastAPI()
    app.include_router(router)
    return app


@pytest.fixture
def client(app):
    return TestClient(app)


# ======================================================
# DEPENDENCY OVERRIDES
# ======================================================

@pytest.fixture(autouse=True)
def allow_roles(app):
    def fake_role(role: str):
        return {"sub": "test-user"}

    app.dependency_overrides[require_role] = fake_role
    yield
    app.dependency_overrides.clear()


def deny_role(role: str):
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Not authorized"
    )


class MockUploadFile:
    filename = "book.jpg"

    async def read(self):
        return b"fake-image-bytes"


@pytest.fixture(autouse=True)
def override_image_upload(app):
    app.dependency_overrides[ImageUploadValidator] = lambda: MockUploadFile()
    yield
    app.dependency_overrides.pop(ImageUploadValidator, None)


# ======================================================
# MOCK BOOK SERVICE
# ======================================================

@pytest.fixture
def mock_book_service():
    service = AsyncMock()

    service.add_book.return_value = {"id": "1", "title": "Clean Code"}
    service.borrow_book.return_value = {"id": "1", "status": "borrowed"}
    service.return_book.return_value = {"id": "1", "status": "available"}
    service.update_book.return_value = {"id": "1", "status": "updated"}
    service.get_book.return_value = {"id": "1", "title": "Clean Code"}
    service.list_books.return_value = [{"id": "1", "title": "Clean Code"}]
    service.delete_book.return_value = None

    return service


# ======================================================
# DONATE BOOK
# ======================================================

def test_donate_book_success(client, mock_book_service):
    with patch("app.api.books.BookService", return_value=mock_book_service):
        response = client.post(
            "/books/donate",
            data={
                "title": "Clean Code",
                "author": "Robert Martin",
                "language": "EN",
                "category": "Programming",
                "isbn": "123456",
            },
            files={"file": ("book.jpg", b"img", "image/jpeg")},
        )

    assert response.status_code == 200
    assert response.json()["message"] == "Book donated successfully"


def test_donate_book_forbidden(app, client):
    app.dependency_overrides[require_role] = deny_role

    response = client.post(
        "/books/donate",
        data={
            "title": "X",
            "author": "Y",
            "language": "EN",
            "category": "Z",
            "isbn": "1",
        },
        files={"file": ("book.jpg", b"img", "image/jpeg")},
    )

    assert response.status_code == 403


# ======================================================
# BORROW BOOK
# ======================================================

def test_borrow_book_success(client, mock_book_service):
    with patch("app.api.books.BookService", return_value=mock_book_service):
        response = client.post("/books/1/borrow")

    assert response.status_code == 200
    assert response.json()["book"]["status"] == "borrowed"


def test_borrow_book_forbidden(app, client):
    app.dependency_overrides[require_role] = deny_role

    response = client.post("/books/1/borrow")
    assert response.status_code == 403


def test_borrow_book_already_borrowed(client):
    conflict_service = AsyncMock()
    conflict_service.borrow_book.side_effect = HTTPException(
        status_code=400,
        detail="Book already borrowed"
    )

    with patch("app.api.books.BookService", return_value=conflict_service):
        response = client.post("/books/1/borrow")

    assert response.status_code == 400
    assert response.json()["detail"] == "Book already borrowed"


# ======================================================
# RETURN BOOK
# ======================================================

def test_return_book_success(client, mock_book_service):
    with patch("app.api.books.BookService", return_value=mock_book_service):
        response = client.post("/books/1/return")

    assert response.status_code == 200
    assert response.json()["book"]["status"] == "available"


def test_return_book_not_borrowed(client):
    conflict_service = AsyncMock()
    conflict_service.return_book.side_effect = HTTPException(
        status_code=400,
        detail="Book is not borrowed"
    )

    with patch("app.api.books.BookService", return_value=conflict_service):
        response = client.post("/books/1/return")

    assert response.status_code == 400


# ======================================================
# UPDATE BOOK
# ======================================================

def test_update_book_success(client, mock_book_service):
    with patch("app.api.books.BookService", return_value=mock_book_service):
        response = client.put(
            "/books/1",
            data={"status": "borrowed", "waiting_list": "u1,u2"}
        )

    assert response.status_code == 200
    assert response.json()["message"] == "Book updated"


def test_update_book_waiting_list_parsed(client, mock_book_service):
    with patch("app.api.books.BookService", return_value=mock_book_service):
        client.put("/books/1", data={"waiting_list": "u1,u2,u3"})

    mock_book_service.update_book.assert_called_once_with(
        book_id="1",
        status=None,
        borrowed_at=None,
        return_date=None,
        waiting_list=["u1", "u2", "u3"],
    )


# ======================================================
# DELETE BOOK
# ======================================================

def test_delete_book(client, mock_book_service):
    with patch("app.api.books.BookService", return_value=mock_book_service):
        response = client.delete("/books/1")

    assert response.status_code == 200
    assert "deleted" in response.json()["message"]


# ======================================================
# GET / LIST BOOKS
# ======================================================

def test_get_book(client, mock_book_service):
    with patch("app.api.books.BookService", return_value=mock_book_service):
        response = client.get("/books/1")

    assert response.status_code == 200
    assert response.json()["book"]["title"] == "Clean Code"


def test_list_books(client, mock_book_service):
    with patch("app.api.books.BookService", return_value=mock_book_service):
        response = client.get("/books/")

    assert response.status_code == 200
    assert len(response.json()["books"]) == 1

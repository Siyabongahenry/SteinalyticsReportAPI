import io
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch

from app.api.book_identifier import router
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
def override_role_dependency(app):
    app.dependency_overrides[require_role] = lambda role=None: None
    yield
    app.dependency_overrides.clear()

class MockUploadFile:
    def __init__(self, content=b"fake-image"):
        self._content = content

    async def read(self):
        return self._content


@pytest.fixture
def override_image_validator(app):
    app.dependency_overrides[ImageUploadValidator] = lambda: MockUploadFile()
    yield
    app.dependency_overrides.pop(ImageUploadValidator, None)


def test_identify_book_success(client, override_image_validator):
    mock_result = {
        "title": "Clean Code",
        "authors": ["Robert C. Martin"],
        "language": "en",
        "categories": ["Programming"],
        "matched_text": "clean code"
    }

    with patch(
        "app.api.book_identifier.service.identify_book",
        return_value=mock_result
    ):
        response = client.post("/books-identifier/identify")

    assert response.status_code == 200
    assert response.json()["title"] == "Clean Code"

def test_identify_book_not_found(client, override_image_validator):
    mock_result = {
        "title": None,
        "matched_text": "random text"
    }

    with patch(
        "app.api.book_identifier.service.identify_book",
        return_value=mock_result
    ):
        response = client.post("/books-identifier/identify")

    assert response.status_code == 200
    assert response.json()["message"] == "No matching book found"

def test_identify_book_exception(client, override_image_validator):
    with patch(
        "app.api.book_identifier.service.identify_book",
        side_effect=Exception("OCR failed")
    ):
        response = client.post("/books-identifier/identify")

    assert response.status_code == 500
    assert "OCR failed" in response.json()["detail"]

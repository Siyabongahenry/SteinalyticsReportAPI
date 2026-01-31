import pytest
from unittest.mock import MagicMock, patch

from app.services.book_identifier import BookIdentifierService


@pytest.fixture
def service():
    svc = BookIdentifierService(region="us-east-1")
    svc.rekognition = MagicMock()
    return svc


@pytest.fixture
def fake_image_bytes():
    return b"fake-image-bytes"


# --------------------------------------------------
# OCR extraction
# --------------------------------------------------
def test_extract_lines_filters_and_ranks(service, fake_image_bytes):
    service.rekognition.detect_text.return_value = {
        "TextDetections": [
            {"DetectedText": "THE NEW BESTSELLER", "Type": "LINE", "Confidence": 98},
            {"DetectedText": "Clean Code", "Type": "LINE", "Confidence": 96},
            {"DetectedText": "Robert C. Martin", "Type": "LINE", "Confidence": 94},
            {"DetectedText": "Hi", "Type": "LINE", "Confidence": 99},
            {"DetectedText": "CLEAN CODE", "Type": "LINE", "Confidence": 97},
        ]
    }

    lines = service.extract_lines(fake_image_bytes)

    assert "Clean Code" in lines
    assert "Robert C. Martin" in lines
    assert "THE NEW BESTSELLER" not in lines  # junk filtered
    assert "Hi" not in lines                  # too short
    assert "CLEAN CODE" not in lines           # all caps filtered


# --------------------------------------------------
# ISBN detection
# --------------------------------------------------
@pytest.mark.parametrize(
    "text,expected",
    [
        ("ISBN: 978-0132350884", "9780132350884"),
        ("9780132350884", "9780132350884"),
        ("ISBN 0132350882", "0132350882"),
        ("no isbn here", None),
    ],
)
def test_detect_isbn(service, text, expected):
    assert service.detect_isbn(text) == expected


# --------------------------------------------------
# Google Books lookup (ISBN)
# --------------------------------------------------
@patch("app.services.book_identifier.requests.get")
def test_lookup_by_isbn_success(mock_get, service):
    mock_get.return_value.json.return_value = {
        "items": [
            {
                "volumeInfo": {
                    "title": "Clean Code",
                    "authors": ["Robert C. Martin"],
                    "language": "en",
                    "categories": ["Programming"],
                    "industryIdentifiers": [
                        {"type": "ISBN_13", "identifier": "9780132350884"}
                    ],
                }
            }
        ]
    }

    book = service.lookup_by_isbn("9780132350884")

    assert book["title"] == "Clean Code"
    assert book["isbn"] == "9780132350884"
    assert book["source"] == "google_books"


# --------------------------------------------------
# Full identification flow (ISBN path)
# --------------------------------------------------
@patch("app.services.book_identifier.requests.get")
def test_identify_book_with_isbn(mock_get, service, fake_image_bytes):
    # Rekognition OCR
    service.rekognition.detect_text.return_value = {
        "TextDetections": [
            {
                "DetectedText": "ISBN 978-0132350884",
                "Type": "LINE",
                "Confidence": 99,
            }
        ]
    }

    # Google Books response
    mock_get.return_value.json.return_value = {
        "items": [
            {
                "volumeInfo": {
                    "title": "Clean Code",
                    "authors": ["Robert C. Martin"],
                    "language": "en",
                    "categories": ["Programming"],
                    "industryIdentifiers": [
                        {"type": "ISBN_13", "identifier": "9780132350884"}
                    ],
                }
            }
        ]
    }

    result = service.identify_book(fake_image_bytes)

    assert result["confidence"] == 0.95
    assert result["title"] == "Clean Code"
    assert result["matched_text"] == "9780132350884"
    assert result["source"] == "google_books"


# --------------------------------------------------
# Failure case
# --------------------------------------------------
def test_identify_book_failure(service, fake_image_bytes):
    service.rekognition.detect_text.return_value = {
        "TextDetections": []
    }

    result = service.identify_book(fake_image_bytes)

    assert result["confidence"] == 0.0
    assert result["title"] is None
    assert result["source"] == "none"

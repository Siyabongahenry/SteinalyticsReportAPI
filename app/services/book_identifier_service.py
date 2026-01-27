import boto3
import requests
from typing import Dict, Any
from app.core.settings import settings


class BookIdentifierService:
    def __init__(self, region: str = "us-east-1"):
        # Initialize AWS Rekognition client
        self.rekognition = boto3.client("rekognition", region_name=region)
        # Load Google Books API key from environment variable
        self.google_api_key = settings.google_books_api_key

    def extract_text(self, image_bytes: bytes) -> str:
        """
        Use AWS Rekognition to detect text from an image.
        Returns a concatenated string of all detected text blocks.
        """
        response = self.rekognition.detect_text(Image={"Bytes": image_bytes})
        detected_texts = [d["DetectedText"] for d in response["TextDetections"]]
        return " ".join(detected_texts)

    def lookup_google_books(self, query: str) -> Dict[str, Any]:
        """
        Query Google Books API using OCR text.
        Returns structured metadata if a match is found.
        """
        r = requests.get(
            "https://www.googleapis.com/books/v1/volumes",
            params={"q": query, "key": self.google_api_key}
        )
        data = r.json()
        if "items" in data and data["items"]:
            book = data["items"][0]["volumeInfo"]
            return {
                "title": book.get("title"),
                "authors": book.get("authors", []),
                "language": book.get("language"),
                "categories": book.get("categories", []),
            }
        return {}

    def lookup_open_library(self, query: str) -> Dict[str, Any]:
        """
        Query Open Library API as a fallback if Google Books has no match.
        Returns structured metadata if a match is found.
        """
        r = requests.get("https://openlibrary.org/search.json", params={"q": query})
        data = r.json()
        if data.get("docs"):
            doc = data["docs"][0]
            return {
                "title": doc.get("title"),
                "authors": doc.get("author_name", []),
                "language": doc.get("language", []),
                "categories": doc.get("subject", []),
            }
        return {}

    def identify_book(self, image_bytes: bytes) -> Dict[str, Any]:
        """
        Full pipeline:
        1. Extract text from image using Rekognition.
        2. Try Google Books API for metadata.
        3. Fallback to Open Library if no match.
        Returns a dictionary with title, authors, language, categories.
        """
        candidate_text = self.extract_text(image_bytes)
        book = self.lookup_google_books(candidate_text)
        if not book:
            book = self.lookup_open_library(candidate_text)
        return {
            "matched_text": candidate_text,
            "title": book.get("title"),
            "authors": book.get("authors", []),
            "language": book.get("language"),
            "categories": book.get("categories", [])
        }

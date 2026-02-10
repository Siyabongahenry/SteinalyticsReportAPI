import boto3
import requests
import re
from typing import Dict, Any, List
from app.core.settings import settings
from app.core.generativeAIConfig import GoogleAIClient

google_ai = GoogleAIClient()

ISBN_REGEX = re.compile(
    r"(97[89][-\s]?\d{1,5}[-\s]?\d{1,7}[-\s]?\d{1,7}[-\s]?\d|"
    r"\d{9}[\dXx])"
)


class BookIdentifierService:
    def __init__(self, region: str = "us-east-1"):
        self.rekognition = boto3.client("rekognition", region_name=region)
        self.google_api_key = settings.google_books_api_key

    # --------------------------------------------------
    # OCR: image → ranked text lines
    # --------------------------------------------------
    def extract_lines(self, image_bytes: bytes) -> List[str]:
        response = self.rekognition.detect_text(Image={"Bytes": image_bytes})

        lines = [
            d["DetectedText"].strip()
            for d in response["TextDetections"]
            if d["Type"] == "LINE" and d["Confidence"] >= 85
        ]

        # Remove obvious junk
        lines = [
            l for l in lines
            if len(l) >= 4
            and not l.isupper()
            and not l.lower().startswith(("the new", "now a", "winner"))
        ]

        return sorted(lines, key=len, reverse=True)[:8]

    # --------------------------------------------------
    # ISBN detection (image-only, highest confidence)
    # --------------------------------------------------
    def detect_isbn(self, text: str) -> str | None:
        match = ISBN_REGEX.search(text.replace("ISBN", "").replace(":", ""))
        return match.group(0).replace("-", "").replace(" ", "") if match else None

    # --------------------------------------------------
    # Google Books (ISBN)
    # --------------------------------------------------
    def lookup_by_isbn(self, isbn: str) -> Dict[str, Any]:
        r = requests.get(
            "https://www.googleapis.com/books/v1/volumes",
            params={"q": f"isbn:{isbn}", "key": self.google_api_key}
        )
        data = r.json()

        if data.get("items"):
            return self.normalize_google(data["items"][0]["volumeInfo"])

        return {}

    # --------------------------------------------------
    # Google Books (Title-only)
    # --------------------------------------------------
    def lookup_by_title(self, title: str) -> Dict[str, Any]:
        r = requests.get(
            "https://www.googleapis.com/books/v1/volumes",
            params={
                "q": f'intitle:"{title}"',
                "key": self.google_api_key,
                "maxResults": 1,
            }
        )

        data = r.json()
        if data.get("items"):
            return self.normalize_google(data["items"][0]["volumeInfo"])

        return {}

    # --------------------------------------------------
    # Open Library fallback
    # --------------------------------------------------
    def lookup_open_library(self, title: str) -> Dict[str, Any]:
        r = requests.get(
            "https://openlibrary.org/search.json",
            params={"title": title, "limit": 1}
        )
        data = r.json()

        if data.get("docs"):
            doc = data["docs"][0]
            return {
                "title": doc.get("title"),
                "authors": doc.get("author_name", []),
                "language": doc.get("language", []),
                "categories": doc.get("subject", []),
                "source": "openlibrary",
            }

        return {}

    # --------------------------------------------------
    # Normalize Google Books
    # --------------------------------------------------
    def normalize_google(self, book: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "title": book.get("title"),
            "authors": book.get("authors", []),
            "language": book.get("language"),
            "categories": book.get("categories", []),
            "isbn": next(
                (
                    i["identifier"]
                    for i in book.get("industryIdentifiers", [])
                    if i["type"] in ("ISBN_13", "ISBN_10")
                ),
                None,
            ),
            "source": "google_books",
        }

    # --------------------------------------------------
    # MAIN: image-only identification
    # --------------------------------------------------
    def identify_book(self, image_bytes: bytes) -> Dict[str, Any]:
        lines = self.extract_lines(image_bytes)
        joined_text = " ".join(lines)

        # 1️⃣ ISBN → near-certain match
        isbn = self.detect_isbn(joined_text)
        if isbn:
            book = self.lookup_by_isbn(isbn)
            if book:
                return {
                    "confidence": 0.95,
                    "matched_text": isbn,
                    **book,
                }

        # 2️⃣ Title inference
        for line in lines:
            book = self.lookup_by_title(line)
            if book:
                return {
                    "confidence": 0.75,
                    "matched_text": line,
                    **book,
                }

        # 3️⃣ Open Library fallback
        for line in lines:
            book = self.lookup_open_library(line)
            if book:
                return {
                    "confidence": 0.6,
                    "matched_text": line,
                    **book,
                }

        # 4️⃣ Honest failure
        return {
            "confidence": 0.0,
            "matched_text": joined_text,
            "title": None,
            "authors": [],
            "language": None,
            "categories": [],
            "source": "none",
        }
    
    def describe_book(title: str = None, author: str = None, sbn: str = None):
        if not title and not author:
            return {"error": "Provide either a title or an author"}

        if title and author:
            prompt = f"Summarize the book '{title}' by {author}."
        elif sbn:
            prompt = f"Summarize the book SBN '{sbn}'."
        else:
            prompt = f"Summarize a book written by {title}."

        summary = google_ai.ask(prompt)

        return {"summary": summary}

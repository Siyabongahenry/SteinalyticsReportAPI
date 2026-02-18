import requests
from typing import Dict, Any, Optional, List
from app.core.settings import settings
from app.core.bedrockAIConfig import BedrockAIClient

bedrock_ai = BedrockAIClient()


class BookIdentifierService:
    def __init__(self):
        self.google_api_key = settings.google_books_api_key

    # --------------------------------------------------
    # Google Books lookup
    # --------------------------------------------------
    def lookup_google(
        self,
        title: str,
        author: Optional[str] = None,
        publish_date: Optional[str] = None,
        publisher: Optional[str] = None,
        language: Optional[str] = None,
        categories: Optional[List[str]] = None,
        series: Optional[str] = None,
        edition: Optional[str] = None,
    ) -> Dict[str, Any]:
        query = f'intitle:"{title}"'
        if author:
            query += f' inauthor:"{author}"'
        if publisher:
            query += f' inpublisher:"{publisher}"'
        if publish_date:
            query += f' {publish_date}'
        if language:
            query += f' language:{language}'
        if categories:
            query += " " + " ".join([f'subject:"{c}"' for c in categories])
        if series:
            query += f' "{series}"'
        if edition:
            query += f' "{edition}"'

        r = requests.get(
            "https://www.googleapis.com/books/v1/volumes",
            params={"q": query, "key": self.google_api_key, "maxResults": 1}
        )
        data = r.json()

        if data.get("items"):
            return self.normalize_google(data["items"][0]["volumeInfo"])
        return {}

    # --------------------------------------------------
    # Open Library fallback
    # --------------------------------------------------
    def lookup_open_library(
        self,
        title: str,
        author: Optional[str] = None,
        publish_date: Optional[str] = None,
        publisher: Optional[str] = None,
        language: Optional[str] = None,
        categories: Optional[List[str]] = None,
        series: Optional[str] = None,
        edition: Optional[str] = None,
    ) -> Dict[str, Any]:
        params = {"title": title, "limit": 1}
        if author:
            params["author"] = author
        if publish_date:
            params["publish_date"] = publish_date
        if publisher:
            params["publisher"] = publisher
        if language:
            params["language"] = language
        if categories:
            params["subject"] = categories[0]  # Open Library supports one subject filter
        if series:
            params["series"] = series
        if edition:
            params["edition"] = edition

        r = requests.get("https://openlibrary.org/search.json", params=params)
        data = r.json()

        if data.get("docs"):
            doc = data["docs"][0]
            return {
                "title": doc.get("title"),
                "authors": doc.get("author_name", []),
                "language": doc.get("language", []),
                "categories": doc.get("subject", []),
                "publish_date": doc.get("first_publish_year"),
                "publisher": doc.get("publisher", [None])[0],
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
            "publish_date": book.get("publishedDate"),
            "publisher": book.get("publisher"),
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
    # MAIN: metadata-only identification
    # --------------------------------------------------
    def identify_book(
        self,
        title: str,
        author: Optional[str] = None,
        isbn: Optional[str] = None,
        publish_date: Optional[str] = None,
        publisher: Optional[str] = None,
        language: Optional[str] = None,
        categories: Optional[List[str]] = None,
        series: Optional[str] = None,
        edition: Optional[str] = None,
    ) -> Dict[str, Any]:
        # Try Google Books first
        book = self.lookup_google(title, author, publish_date, publisher, language, categories, series, edition)
        if book:
            return {"confidence": 0.9, **book}

        # Fallback to Open Library
        book = self.lookup_open_library(title, author, publish_date, publisher, language, categories, series, edition)
        if book:
            return {"confidence": 0.7, **book}

        # Failure
        return {
            "confidence": 0.0,
            "title": title,
            "authors": [author] if author else [],
            "publish_date": publish_date,
            "publisher": publisher,
            "language": language,
            "categories": categories or [],
            "series": series,
            "edition": edition,
            "source": "none",
        }

    # --------------------------------------------------
    # Summarize book using AI
    # --------------------------------------------------
    def describe_book(self, title: Optional[str] = None, author: Optional[str] = None, isbn: Optional[str] = None):
        if not title and not author and not isbn:
            return {"error": "Provide a title, author, or ISBN"}

        if title and author:
            prompt = f"Summarize the book '{title}' by {author}."
        elif isbn:
            prompt = f"Summarize the book with ISBN '{isbn}'."
        else:
            prompt = f"Summarize the book titled '{title}'."

        summary = bedrock_ai.ask(prompt)

        return {"summary": summary}

import uuid
from datetime import datetime, timezone
import boto3
from app.core.dynamoDB import get_table
from app.core.settings import settings

class BookService:
    def __init__(self, table_name: str = settings.books_table):
        self.table = get_table(table_name)
        self.s3 = boto3.client("s3")
        self.bucket = settings.library_bucket
        self.books_domain = settings.books_domain

    async def upload_to_s3(self, file, filename: str) -> str:
        """Upload file to S3 and return public CloudFront URL."""

        key = f"books/{filename}"

        self.s3.upload_fileobj(
            file.file,
            self.bucket,
            key,
            ExtraArgs={
                "ContentType": file.content_type
            }
        )

        # Return CloudFront-backed public URL
        return f"{self.books_domain}/{filename}"



    async def add_book(self, title, author, language, category, isbn, file, user_id):
        file_ext = file.filename.split(".")[-1]
        unique_filename = f"{uuid.uuid4()}.{file_ext}"

        file_url = await self.upload_to_s3(file, unique_filename)

        item = {
            "id": str(uuid.uuid4()),
            "title": title,
            "author": author,
            "language": language,
            "category": category,
            "isbn": isbn,
            "file_url": file_url,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "created_by": user_id,
            "status": "available",
            "borrowed_at": None,
            "return_date": None,
            "waiting_list": [],
        }

        self.table.put_item(Item=item)
        return item

    async def get_book(self, book_id: str):
        response = self.table.get_item(Key={"id": book_id})
        return response.get("Item")

    async def delete_book(self, book_id: str):
        self.table.delete_item(Key={"id": book_id})

    async def list_books(self):
        """Return all books in the table."""
        response = self.table.scan()
        return response.get("Items", [])

    # --------------------
    # Borrow Book
    # --------------------
    async def borrow_book(self, book_id: str, user_id: str, borrowed_at: str, return_date: str):
        """Mark a book as borrowed by a user."""
        response = self.table.update_item(
            Key={"id": book_id},
            UpdateExpression="SET #status = :status, borrowed_at = :borrowed_at, return_date = :return_date, created_by = :user_id",
            ExpressionAttributeNames={"#status": "status"},
            ExpressionAttributeValues={
                ":status": "borrowed",
                ":borrowed_at": borrowed_at,
                ":return_date": return_date,
                ":user_id": user_id,
            },
            ReturnValues="ALL_NEW",
        )
        return response.get("Attributes")

    # --------------------
    # Return Book
    # --------------------
    async def return_book(self, book_id: str, user_id: str, returned_at: str):
        """Mark a book as returned and available again."""
        response = self.table.update_item(
            Key={"id": book_id},
            UpdateExpression="SET #status = :status, borrowed_at = :borrowed_at, return_date = :return_date",
            ExpressionAttributeNames={"#status": "status"},
            ExpressionAttributeValues={
                ":status": "available",
                ":borrowed_at": None,
                ":return_date": None,
            },
            ReturnValues="ALL_NEW",
        )
        return response.get("Attributes")

    # --------------------
    # Update Book (generic admin use)
    # --------------------
    async def update_book(self, book_id: str, status=None, borrowed_at=None, return_date=None, waiting_list=None):
        """Update book fields (admin use)."""
        update_expr = []
        expr_attr_values = {}
        expr_attr_names = {}

        if status is not None:
            update_expr.append("#status = :status")
            expr_attr_values[":status"] = status
            expr_attr_names["#status"] = "status"

        if borrowed_at is not None:
            update_expr.append("borrowed_at = :borrowed_at")
            expr_attr_values[":borrowed_at"] = borrowed_at

        if return_date is not None:
            update_expr.append("return_date = :return_date")
            expr_attr_values[":return_date"] = return_date

        if waiting_list is not None:
            update_expr.append("waiting_list = :waiting_list")
            expr_attr_values[":waiting_list"] = waiting_list

        if not update_expr:
            return await self.get_book(book_id)

        response = self.table.update_item(
            Key={"id": book_id},
            UpdateExpression="SET " + ", ".join(update_expr),
            ExpressionAttributeValues=expr_attr_values,
            ExpressionAttributeNames=expr_attr_names if expr_attr_names else None,
            ReturnValues="ALL_NEW",
        )
        return response.get("Attributes")

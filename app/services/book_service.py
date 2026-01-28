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

    async def upload_to_s3(self, file, filename: str) -> str:
        """Upload file to S3 and return public URL."""
        self.s3.upload_fileobj(
            file.file,
            self.bucket,
            filename,
            ExtraArgs={"ACL": "public-read"}  # or use signed URLs
        )
        return f"https://{self.bucket}.s3.amazonaws.com/{filename}"

    async def add_book(self, title, author, language, category, isbn, file, user_id):
        # Generate UUID filename
        file_ext = file.filename.split(".")[-1]
        unique_filename = f"{uuid.uuid4()}.{file_ext}"

        # Upload file to S3
        file_url = await self.upload_to_s3(file, unique_filename)

        # Create metadata item
        item = {
            "id": str(uuid.uuid4()),
            "title": title,
            "author": author,
            "language": language,
            "category": category,
            "isbn": isbn,
            "file_url": file_url,  # 👈 store URL, not file bytes
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

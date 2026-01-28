from app.core.dynamoDB import get_table
from app.core.settings import settings

class BookService:
    def __init__(self, table_name: str = settings.books_table):
        self.table = get_table(table_name)

    async def add_book(self, item: dict):
        self.table.put_item(Item=item)
        return item

    async def get_book(self, book_id: str):
        response = self.table.get_item(Key={"id": book_id})
        return response.get("Item")

    async def delete_book(self, book_id: str):
        self.table.delete_item(Key={"id": book_id})

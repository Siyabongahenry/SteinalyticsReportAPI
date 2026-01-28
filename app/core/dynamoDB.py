import boto3
from app.core.settings import settings

# Create a single DynamoDB resource
dynamodb = boto3.resource("dynamodb", region_name=settings.region)

def get_table(table_name: str):
    """
    Return a DynamoDB Table object for the given table name.
    """
    return dynamodb.Table(table_name)

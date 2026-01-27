import boto3
from app.core.settings import settings

# DynamoDB resource
dynamodb = boto3.resource("dynamodb", region_name=settings.region)

# Table reference
table = dynamodb.Table(settings.email_organizer_table)

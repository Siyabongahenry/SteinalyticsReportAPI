import boto3
from app.core.config import settings

s3_client = boto3.client(
    "s3",
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    region_name=settings.AWS_REGION,
)

def upload_file_to_s3(file_obj, file_name: str):
    s3_client.upload_fileobj(
        file_obj,
        settings.AWS_S3_BUCKET,
        file_name,
        ExtraArgs={"ContentType": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"},
    )

    return f"s3://{settings.AWS_S3_BUCKET}/{file_name}"

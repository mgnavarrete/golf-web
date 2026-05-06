import boto3
from django.conf import settings


def upload_bytes_to_s3(file_bytes: bytes, object_path: str, content_type: str = "image/jpeg") -> str:
    s3 = boto3.client(
        "s3",
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_S3_REGION_NAME,
    )

    s3.put_object(
        Bucket=settings.AWS_STORAGE_BUCKET_NAME,
        Key=object_path,
        Body=file_bytes,
        ContentType=content_type,
    )
    return object_path


def public_s3_url(object_path: str) -> str:
    return f"https://{settings.AWS_S3_CUSTOM_DOMAIN}/{object_path}"

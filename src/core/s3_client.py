import boto3
from botocore.client import Config

from src.core.config import get_settings

settings = get_settings()
s3_client = boto3.client(
    "s3",
    endpoint_url=settings.s3_endpoint_url,
    aws_access_key_id=settings.s3_access_key,
    aws_secret_access_key=settings.s3_secret_key,
    region_name=settings.s3_region,
    config=Config(
        signature_version="s3v4",
        s3={"addressing_style": "path"},
    ),
)


def ensure_bucket() -> None:
    buckets = s3_client.list_buckets()["Buckets"]

    if any(bucket["Name"] == settings.s3_bucket_name for bucket in buckets):
        return

    s3_client.create_bucket(Bucket=settings.s3_bucket_name)

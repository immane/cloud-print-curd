import boto3
from botocore.exceptions import ClientError

from src.app.config import settings


def get_s3_client():
    endpoint_url = settings.storage_endpoint
    if not settings.storage_use_ssl and endpoint_url.startswith("https://"):
        endpoint_url = endpoint_url.replace("https://", "http://", 1)
    elif not endpoint_url.startswith("http"):
        endpoint_url = f"https://{endpoint_url}" if settings.storage_use_ssl else f"http://{endpoint_url}"

    return boto3.client(
        "s3",
        endpoint_url=endpoint_url,
        aws_access_key_id=settings.storage_access_key,
        aws_secret_access_key=settings.storage_secret_key,
        region_name=settings.storage_region,
        use_ssl=settings.storage_use_ssl,
        verify=settings.storage_use_ssl,
    )


def ensure_bucket():
    client = get_s3_client()
    buckets = [settings.storage_bucket, settings.storage_bucket_private]
    for bucket in buckets:
        if not bucket:
            continue
        try:
            client.head_bucket(Bucket=bucket)
        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            if error_code in ("404", "NoSuchBucket"):
                if settings.storage_region != "us-east-1":
                    client.create_bucket(
                        Bucket=bucket,
                        CreateBucketConfiguration={"LocationConstraint": settings.storage_region},
                    )
                else:
                    client.create_bucket(Bucket=bucket)
            else:
                raise


def create_presigned_post(storage_key: str, content_type: str, max_size: int):
    client = get_s3_client()
    response = client.generate_presigned_post(
        Bucket=settings.storage_bucket,
        Key=storage_key,
        Fields={"Content-Type": content_type},
        Conditions=[
            {"Content-Type": content_type},
            ["content-length-range", 0, max_size],
        ],
        ExpiresIn=600,
    )
    return {"url": response["url"], "fields": response["fields"]}


def create_presigned_download_url(storage_key: str, expiration: int = 3600):
    client = get_s3_client()
    url = client.generate_presigned_url(
        "get_object",
        Params={
            "Bucket": settings.storage_bucket,
            "Key": storage_key,
            "ResponseContentDisposition": "attachment",
        },
        ExpiresIn=expiration,
    )
    return url


def verify_object(storage_key: str) -> bool:
    client = get_s3_client()
    try:
        client.head_object(Bucket=settings.storage_bucket, Key=storage_key)
        return True
    except ClientError as e:
        if e.response["Error"]["Code"] == "404":
            return False
        raise


def get_object_info(storage_key: str):
    client = get_s3_client()
    response = client.head_object(Bucket=settings.storage_bucket, Key=storage_key)
    return {
        "size": response.get("ContentLength", 0),
        "content_type": response.get("ContentType"),
        "etag": response.get("ETag", "").strip('"'),
    }


def delete_object(storage_key: str):
    client = get_s3_client()
    client.delete_object(Bucket=settings.storage_bucket, Key=storage_key)

import logging
from pathlib import Path
import boto3
from botocore.exceptions import ClientError
from .config import config

logger = logging.getLogger(__name__)

class S3StorageManager:
    """Handles S3 object storage operations with AWS or local MinIO compatibility."""

    def __init__(self):
        client_kwargs = {
            "aws_access_key_id": config.aws_access_key_id,
            "aws_secret_access_key": config.aws_secret_access_key,
            "region_name": config.aws_region,
        }
        if config.s3_endpoint_url:
            client_kwargs["endpoint_url"] = config.s3_endpoint_url

        self.s3 = boto3.client("s3", **client_kwargs)

    def ensure_bucket_exists(self, bucket_name: str) -> None:
        try:
            self.s3.head_bucket(Bucket=bucket_name)
        except ClientError:
            logger.info("Creating bucket: %s", bucket_name)
            create_kwargs = {"Bucket": bucket_name}
            if config.aws_region != "us-east-1" and not config.s3_endpoint_url:
                create_kwargs["CreateBucketConfiguration"] = {"LocationConstraint": config.aws_region}
            self.s3.create_bucket(**create_kwargs)

    def upload_file(self, local_path: Path | str, bucket_name: str, object_key: str, content_type: str = "application/octet-stream") -> str:
        local_path = Path(local_path)
        if not local_path.exists():
            raise FileNotFoundError(f"File not found: {local_path}")

        self.ensure_bucket_exists(bucket_name)
        extra_args = {"ContentType": content_type}
        self.s3.upload_file(str(local_path), bucket_name, object_key, ExtraArgs=extra_args)
        logger.info("Uploaded %s to s3://%s/%s", local_path.name, bucket_name, object_key)
        return f"s3://{bucket_name}/{object_key}"

    def upload_bytes(self, data: bytes, bucket_name: str, object_key: str, content_type: str = "application/octet-stream") -> str:
        self.ensure_bucket_exists(bucket_name)
        self.s3.put_object(
            Bucket=bucket_name,
            Key=object_key,
            Body=data,
            ContentType=content_type
        )
        return f"s3://{bucket_name}/{object_key}"

    def download_file(self, bucket_name: str, object_key: str, target_path: Path | str) -> Path:
        target_path = Path(target_path)
        target_path.parent.mkdir(parents=True, exist_ok=True)
        self.s3.download_file(bucket_name, object_key, str(target_path))
        return target_path

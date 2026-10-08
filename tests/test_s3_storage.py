import pytest
from moto import mock_aws
import boto3
from emissions_pipeline.s3_client import S3StorageManager

@mock_aws
def test_s3_upload_and_download(tmp_path):
    s3_mgr = S3StorageManager()
    bucket = "test-emissions-bucket"
    s3_mgr.ensure_bucket_exists(bucket)

    sample_file = tmp_path / "test_plume.parquet"
    sample_file.write_bytes(b"PAR1_DUMMY_BINARY_DATA")

    uri = s3_mgr.upload_file(sample_file, bucket, "2026/test.parquet")
    assert uri == f"s3://{bucket}/2026/test.parquet"

    downloaded = tmp_path / "downloaded.parquet"
    s3_mgr.download_file(bucket, "2026/test.parquet", downloaded)
    assert downloaded.read_bytes() == b"PAR1_DUMMY_BINARY_DATA"

import os
from pydantic import Field
from pydantic_settings import BaseSettings

class PipelineConfig(BaseSettings):
    # Database
    db_host: str = Field(default_factory=lambda: os.getenv("DB_HOST", "localhost"))
    db_port: int = Field(default_factory=lambda: int(os.getenv("DB_PORT", "5432")))
    db_name: str = Field(default_factory=lambda: os.getenv("DB_NAME", "emissions_db"))
    db_user: str = Field(default_factory=lambda: os.getenv("DB_USER", "spatial_admin"))
    db_password: str = Field(default_factory=lambda: os.getenv("DB_PASSWORD", "spatial_secure_pwd"))

    # AWS S3 / MinIO Configuration
    aws_access_key_id: str = Field(default_factory=lambda: os.getenv("AWS_ACCESS_KEY_ID", "minioadmin"))
    aws_secret_access_key: str = Field(default_factory=lambda: os.getenv("AWS_SECRET_ACCESS_KEY", "miniopassword"))
    aws_region: str = Field(default_factory=lambda: os.getenv("AWS_DEFAULT_REGION", "ca-central-1"))
    s3_endpoint_url: str | None = Field(default_factory=lambda: os.getenv("S3_ENDPOINT_URL", "http://localhost:9000"))
    s3_bucket_raw: str = Field(default_factory=lambda: os.getenv("S3_BUCKET_RAW", "emissions-raw-observations"))
    s3_bucket_processed: str = Field(default_factory=lambda: os.getenv("S3_BUCKET_PROCESSED", "emissions-analytical-geoparquet"))

    @property
    def db_connection_url(self) -> str:
        return f"postgresql://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"

config = PipelineConfig()

import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_env: str = "development"
    app_name: str = "cloud-print"
    debug: bool = True

    database_url: str = "mysql+aiomysql://print_user:print_pass@localhost:3306/cloud_print"
    database_url_sync: str = "mysql+pymysql://print_user:print_pass@localhost:3306/cloud_print"
    redis_url: str = "redis://localhost:6379/0"

    jwt_secret: str = "dev-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60
    jwt_refresh_expire_days: int = 30

    storage_provider: str = "s3"
    storage_endpoint: str = "http://localhost:9000"
    storage_region: str = "us-east-1"
    storage_access_key: str = "minioadmin"
    storage_secret_key: str = "minioadmin"
    storage_bucket: str = "cloud-print-uploads"
    storage_bucket_private: str = "cloud-print-private"
    storage_use_ssl: bool = False

    wechat_app_id: str = ""
    wechat_app_secret: str = ""
    wechat_mch_id: str = ""
    wechat_mch_api_v3_key: str = ""
    wechat_mch_private_key_path: str = ""
    wechat_platform_cert_path: str = ""
    wechat_notify_url: str = ""

    sentry_dsn: str = ""
    log_level: str = "INFO"

    file_retention_days: int = 365
    max_upload_size_mb: int = 50
    allowed_content_types: str = "application/pdf,image/jpeg,image/png,image/tiff,application/msword,application/vnd.openxmlformats-officedocument.wordprocessingml.document"

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()

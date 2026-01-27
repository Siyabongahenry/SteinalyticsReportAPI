from typing import Optional
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Required strings with defaults
    core_origins: str = ""
    storage_backend: str = "local"
    oidc_issuer: str = ""
    oidc_audience: str = ""
    email_organizer_table = ""

    # Optional strings (can be None)
    bucket_name: Optional[str] = None
    region: Optional[str] = None

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"  # Optional: ensures correct encoding

# Instantiate settings
settings = Settings()

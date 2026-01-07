from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    bucket_name: str = "local"
    storage_backend: str | None = None
    region: str | None = None

    class Config:
        env_file = ".env"

settings = Settings()

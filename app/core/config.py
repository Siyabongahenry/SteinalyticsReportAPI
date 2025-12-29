from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    bucket_name: str

    class Config:
        env_file = ".env"

settings = Settings()

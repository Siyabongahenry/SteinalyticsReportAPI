from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    core_origins: str =""
    bucket_name:str | None = None 
    storage_backend: str = "local"
    region: str | None = None
    oidc_issuer: str =""
    oidc_audience: str =""
   

    class Config:
        env_file = ".env"

settings = Settings()

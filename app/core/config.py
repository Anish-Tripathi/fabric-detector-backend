from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # App
    APP_NAME: str = "Fabric Defect Detection API"
    APP_VERSION: str = "1.0.0"

    # Security
    API_KEY: str = "mysecret123"

    # Model
    MODEL_PATH: str = "model.keras"

    # CORS — comma-separated origins in .env, e.g. "http://localhost:3000,https://myfrontend.com"
    ALLOWED_ORIGINS: List[str] = ["*"]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()

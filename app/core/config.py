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

    # CORS (UPDATED ONLY THIS PART)
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8080"]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()

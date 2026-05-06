from pydantic_settings import BaseSettings
from typing import List, Optional


class Settings(BaseSettings):
    # App
    APP_NAME: str = "Fabric Defect Detection API"
    APP_VERSION: str = "1.0.0"

    # Security
    API_KEY: str = "mysecret123"

    # Model (commented out - using Gemini instead)
    # MODEL_PATH: str = "model_packed.tflite"

    # Gemini API - ADD THIS FIELD
    GEMINI_API_KEY: Optional[str] = None  # This matches your .env variable

    # CORS
    ALLOWED_ORIGINS: List[str] = [
        "https://fabric-detector.vercel.app",
        "http://localhost:8080",
        "http://localhost:3000",
        "http://localhost:5173",
    ]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"  # This will ignore any extra fields instead of forbidding them


settings = Settings()

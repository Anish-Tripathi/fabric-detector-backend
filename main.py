from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from app.core.config import settings
from app.core.model import model_manager
from app.routes import predict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: initialize model (no load_model needed for Gemini)
    logger.info("Initializing ML model...")
    if model_manager.is_loaded():
        if model_manager._gemini_model:
            logger.info("Gemini model ready")
        else:
            logger.info("Running in mock mode (no Gemini API key)")
    else:
        logger.warning("Model not ready")
    yield
    # Shutdown
    logger.info("Shutting down...")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Fabric Defect Detection API powered by Google Gemini AI",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(predict.router, prefix="/api/v1", tags=["Prediction"])


@app.get("/", tags=["Health"])
def root():
    return {
        "message": "Fabric Defect Detection API Running",
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "model_type": "Gemini AI" if model_manager._gemini_model else "Mock Mode",
    }


@app.get("/health", tags=["Health"])
def health_check():
    return {
        "status": "ok",
        "model_loaded": model_manager.is_loaded(),
        "gemini_enabled": model_manager._gemini_model is not None,
    }

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from PIL import Image
import io

from app.core.security import verify_api_key
from app.core.model import model_manager
from app.schema.predict import PredictionResponse, ErrorResponse

router = APIRouter()

ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp", "image/bmp"}


@router.post(
    "/predict",
    response_model=PredictionResponse,
    responses={
        401: {"model": ErrorResponse, "description": "Unauthorized"},
        422: {"model": ErrorResponse, "description": "Invalid image"},
    },
    summary="Predict fabric defect",
    description="Upload a fabric image to classify it as **Good** or **Defective**.",
)
async def predict(
    file: UploadFile = File(..., description="Fabric image (JPEG / PNG / WebP / BMP)"),
    _: str = Depends(verify_api_key),
):
    # Validate content type
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Unsupported file type '{file.content_type}'. Allowed: {', '.join(ALLOWED_CONTENT_TYPES)}",
        )

    # Read and decode image
    contents = await file.read()
    try:
        image = Image.open(io.BytesIO(contents)).convert("RGB")
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Could not decode image. Please upload a valid image file.",
        )

    # Run inference
    result = model_manager.predict(image)
    return PredictionResponse(**result)

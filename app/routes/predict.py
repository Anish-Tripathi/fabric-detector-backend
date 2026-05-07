from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from PIL import Image
import io
import os
import google.generativeai as genai
from typing import Dict, Any, Literal
from pydantic import BaseModel

from app.core.security import verify_api_key

router = APIRouter()

ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp", "image/bmp"}


# Define ErrorResponse model
class ErrorResponse(BaseModel):
    detail: str


# Define PredictionResponse model
class PredictionResponse(BaseModel):
    prediction: Literal["Good", "Defective"]
    defect_type: Literal["None", "Hole", "Oil Spot", "Objects", "Thread Error"]
    severity: str  # Will be the subclass name based on confidence
    confidence: float  # Overall prediction confidence (0-1)


# Configure Gemini directly with environment variable
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    gemini_model = genai.GenerativeModel("gemini-2.5-flash")
    print("Gemini API configured successfully")
else:
    gemini_model = None


def analyze_with_gemini(image: Image.Image) -> Dict[str, Any]:
    """Analyze fabric image using Gemini LLM."""

    # Convert PIL image to bytes
    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format="PNG")
    img_byte_arr = img_byte_arr.getvalue()

    # Simplified prompt
    prompt = """You are a fabric defect detection expert. Analyze this fabric image and classify it according to the following rules:

CLASSIFICATION RULES:
1. First determine if the fabric is "Good" or "Defective"

2. If Defective, identify ONE of these defect types:
   - Hole (any opening, tear, or puncture)
   - Oil Spot (oil, grease, or liquid contamination)
   - Objects (foreign objects, debris, or particles)
   - Thread Error (weaving issues, yarn misalignment, thread distortion, fraying)

3. Set confidence score from 0.00 to 1.00 based on how certain you are

Return ONLY valid JSON (no markdown, no other text) in this exact structure:
{
    "prediction": "Good" or "Defective",
    "defect_type": "None" or "Hole" or "Oil Spot" or "Objects" or "Thread Error",
    "confidence": 0.00 to 1.00
}

Do not include any additional fields. Return only these three fields in JSON format."""

    try:
        if gemini_model:
            # Call Gemini API
            response = gemini_model.generate_content(
                [prompt, {"mime_type": "image/png", "data": img_byte_arr}]
            )

            # Parse JSON response
            import json

            response_text = response.text.strip()
            # Remove markdown code blocks if present
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.startswith("```"):
                response_text = response_text[3:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]

            result = json.loads(response_text.strip())
        else:
            # Mock response for testing without API key
            result = get_mock_analysis(image)

        # Calculate severity subclass based on confidence
        result["severity"] = calculate_severity_subclass(
            result["prediction"], result["defect_type"], result["confidence"]
        )

        return result

    except Exception as e:
        print(f"Gemini analysis error: {e}")
        # Fallback to mock analysis
        mock_result = get_mock_analysis(image)
        mock_result["severity"] = calculate_severity_subclass(
            mock_result["prediction"],
            mock_result["defect_type"],
            mock_result["confidence"],
        )
        return mock_result


def calculate_severity_subclass(
    prediction: str, defect_type: str, confidence: float
) -> str:
    """Calculate severity subclass based on defect type and confidence score."""

    if prediction == "Good":
        return "None"

    # Convert confidence to percentage for comparison
    confidence_pct = confidence * 100

    # Severity mapping for each defect type
    severity_map = {
        "Hole": {
            (0, 25): "Minor Pinhole",
            (25, 75): "Moderate Tear",
            (75, 101): "Severe Fabric Hole",
        },
        "Oil Spot": {
            (0, 25): "Light Stain",
            (25, 75): "Visible Oil Spot",
            (75, 101): "Heavy Oil Contamination",
        },
        "Objects": {
            (0, 25): "Small Particle",
            (25, 75): "Surface Contamination",
            (75, 101): "Embedded Foreign Object",
        },
        "Thread Error": {
            (0, 25): "Slight Yarn Misalignment",
            (25, 75): "Thread Distortion",
            (75, 101): "Fraying",
        },
    }

    # Get the appropriate severity range for the defect type
    if defect_type in severity_map:
        ranges = severity_map[defect_type]
        for (low, high), severity in ranges.items():
            if low <= confidence_pct < high:
                return severity

    # Default fallback
    return "Unknown"


def get_mock_analysis(image: Image.Image) -> Dict[str, Any]:
    """Generate mock analysis when Gemini is unavailable."""
    # Get image basic properties for deterministic mock
    width, height = image.size
    img_hash = (width * height) % 1000

    # Deterministic mock based on image hash (for testing)
    is_defective = img_hash % 3 == 0  # ~33% defective rate for testing

    if is_defective:
        defect_types = ["Hole", "Oil Spot", "Objects", "Thread Error"]
        defect_type = defect_types[img_hash % len(defect_types)]
        confidence = 0.60 + (img_hash % 40) / 100  # Range: 0.60-0.99
    else:
        defect_type = "None"
        confidence = 0.80 + (img_hash % 20) / 100  # Range: 0.80-0.99

    return {
        "prediction": "Defective" if is_defective else "Good",
        "defect_type": defect_type,
        "confidence": confidence,
    }


@router.options("/predict")
async def predict_options():
    """Handle CORS preflight without auth check."""
    return {}


@router.post(
    "/predict",
    response_model=PredictionResponse,
    responses={
        401: {"model": ErrorResponse, "description": "Unauthorized"},
        422: {"model": ErrorResponse, "description": "Invalid image"},
    },
    summary="Predict fabric defect",
    description="Upload a fabric image to classify it as **Good** or **Defective** with detailed analysis.",
)
async def predict(
    file: UploadFile = File(..., description="Fabric image (JPEG / PNG / WebP / BMP)"),
    _: str = Depends(verify_api_key),
):
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Unsupported file type '{file.content_type}'. Allowed: {', '.join(ALLOWED_CONTENT_TYPES)}",
        )

    contents = await file.read()
    try:
        image = Image.open(io.BytesIO(contents)).convert("RGB")
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Could not decode image. Please upload a valid image file.",
        )

    # Use Gemini for analysis
    analysis_result = analyze_with_gemini(image)

    # Format response to match frontend expectations
    return PredictionResponse(**analysis_result)

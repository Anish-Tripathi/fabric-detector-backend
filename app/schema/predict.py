from pydantic import BaseModel


class PredictionResponse(BaseModel):
    prediction: str  # "Good" | "Defective"
    confidence: float  # 0.0 – 1.0

    model_config = {
        "json_schema_extra": {
            "examples": [
                {"prediction": "Defective", "confidence": 0.87},
                {"prediction": "Good", "confidence": 0.93},
            ]
        }
    }


class ErrorResponse(BaseModel):
    detail: str

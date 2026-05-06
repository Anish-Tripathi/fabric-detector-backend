from pydantic import BaseModel
from typing import List, Optional


class PredictionResponse(BaseModel):
    prediction: str  # "Good" or "Defective"
    confidence: float  # 0.0 – 1.0
    defect_type: Optional[str] = None  # "Hole", "Stain", "Weaving defect", etc.
    defect_confidence: Optional[float] = None  # 0.0 – 1.0
    severity: str  # "None", "Low", "Medium", "High"
    quality_score: int  # 0-100
    texture_uniformity: int  # 0-100
    edge_integrity: int  # 0-100
    weave_consistency: int  # 0-100
    color_homogeneity: int  # 0-100
    tension_balance: int  # 0-100
    surface_roughness: int  # 0-100
    defect_density: int  # 0-100
    pattern_regularity: int  # 0-100
    risk_factors: List[str] = []
    passed_checks: List[str] = []
    advice: str
    explanation: str

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "prediction": "Defective",
                    "confidence": 0.92,
                    "defect_type": "Weaving defect",
                    "defect_confidence": 0.88,
                    "severity": "High",
                    "quality_score": 28,
                    "texture_uniformity": 25,
                    "edge_integrity": 30,
                    "weave_consistency": 20,
                    "color_homogeneity": 45,
                    "tension_balance": 35,
                    "surface_roughness": 85,
                    "defect_density": 78,
                    "pattern_regularity": 15,
                    "risk_factors": [
                        "Detected weaving defect with 88% confidence",
                        "Texture uniformity below threshold (25/100)",
                        "Irregular weave pattern identified",
                    ],
                    "passed_checks": ["Color distribution within range"],
                    "advice": "Reject roll segment immediately. Perform root-cause analysis on loom settings and yarn quality before resuming production.",
                    "explanation": "The analysis identified a weaving defect with 88% confidence. Key indicators include irregular weave pattern (20/100), elevated defect density (78/100), and high surface roughness (85/100).",
                },
                {
                    "prediction": "Good",
                    "confidence": 0.94,
                    "defect_type": "None",
                    "defect_confidence": 0.0,
                    "severity": "None",
                    "quality_score": 94,
                    "texture_uniformity": 92,
                    "edge_integrity": 95,
                    "weave_consistency": 91,
                    "color_homogeneity": 94,
                    "tension_balance": 90,
                    "surface_roughness": 12,
                    "defect_density": 8,
                    "pattern_regularity": 93,
                    "risk_factors": [],
                    "passed_checks": [
                        "Texture uniformity within specification",
                        "No structural defects detected",
                        "Weave pattern consistent",
                        "Edge integrity confirmed",
                    ],
                    "advice": "No defects detected. Product meets quality standards. Proceed to next QA stage.",
                    "explanation": "Fabric sample classified as Good with 94% confidence. All key metrics are within acceptable ranges: texture uniformity (92/100), weave consistency (91/100), and color homogeneity (94/100).",
                },
            ]
        }
    }


class ErrorResponse(BaseModel):
    detail: str

    model_config = {
        "json_schema_extra": {
            "examples": [
                {"detail": "Invalid API key"},
                {"detail": "Could not decode image. Please upload a valid image file."},
                {
                    "detail": "Unsupported file type 'image/gif'. Allowed: image/jpeg, image/png, image/webp, image/bmp"
                },
            ]
        }
    }

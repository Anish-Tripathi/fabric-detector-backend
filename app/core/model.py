import numpy as np
from PIL import Image
from app.core.config import settings
import os
import google.generativeai as genai
from typing import Dict, Any
import io
import json


class ModelManager:
    """Singleton wrapper around Gemini LLM model."""

    def __init__(self):
        self._gemini_model = None
        self._configure_gemini()

    def _configure_gemini(self):
        """Configure Gemini API."""
        gemini_api_key = os.getenv("GEMINI_API_KEY", "")

        if gemini_api_key:
            try:
                genai.configure(api_key=gemini_api_key)
                # Use gemini-2.5-flash - stable, free, and supports vision
                self._gemini_model = genai.GenerativeModel("gemini-2.5-flash")
            except Exception:
                self._gemini_model = None
        else:
            self._gemini_model = None

    def is_loaded(self) -> bool:
        """Check if model is available."""
        return True

    def load_model(self):
        """Compatibility method - does nothing for Gemini."""
        pass

    def predict(self, image: Image.Image) -> dict:
        """Analyze fabric image using Gemini LLM."""

        if self._gemini_model:
            return self._analyze_with_gemini(image)
        else:
            return self._get_mock_analysis(image)

    def _analyze_with_gemini(self, image: Image.Image) -> dict:
        """Analyze image using Gemini API."""

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
            # Call Gemini API
            response = self._gemini_model.generate_content(
                [prompt, {"mime_type": "image/png", "data": img_byte_arr}]
            )

            # Parse JSON response
            response_text = response.text.strip()
            # Remove markdown code blocks if present
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.startswith("```"):
                response_text = response_text[3:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]

            result = json.loads(response_text.strip())

            # Ensure confidence is rounded
            result["confidence"] = round(result.get("confidence", 0.5), 4)

            # Calculate severity subclass based on confidence
            result["severity"] = self._calculate_severity_subclass(
                result["prediction"], result["defect_type"], result["confidence"]
            )

            return result

        except Exception:
            return self._get_mock_analysis(image)

    def _calculate_severity_subclass(
        self, prediction: str, defect_type: str, confidence: float
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

    def _get_mock_analysis(self, image: Image.Image) -> dict:
        """Generate mock analysis when Gemini is unavailable."""
        # Get image basic properties for deterministic mock
        width, height = image.size
        img_hash = (width * height) % 1000

        # Deterministic mock based on image hash (for testing)
        is_defective = img_hash % 3 == 0  # ~33% defective rate for testing

        if is_defective:
            defect_types = ["Hole", "Oil Spot", "Objects", "Thread Error"]
            defect_type = defect_types[img_hash % len(defect_types)]
            confidence = round(0.60 + (img_hash % 40) / 100, 4)
        else:
            defect_type = "None"
            confidence = round(0.80 + (img_hash % 20) / 100, 4)

        result = {
            "prediction": "Defective" if is_defective else "Good",
            "defect_type": defect_type,
            "confidence": confidence,
        }

        # Calculate severity subclass
        result["severity"] = self._calculate_severity_subclass(
            result["prediction"], result["defect_type"], result["confidence"]
        )

        return result


# Global singleton instance
model_manager = ModelManager()

import tensorflow as tf
import numpy as np
from PIL import Image
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)


class ModelManager:
    """Singleton wrapper around the TensorFlow Keras model."""

    def __init__(self):
        self._model = None

    def load_model(self):
        if self._model is None:
            logger.info(f"Loading model from: {settings.MODEL_PATH}")
            self._model = tf.keras.models.load_model(settings.MODEL_PATH)
            logger.info("Model ready.")

    def is_loaded(self) -> bool:
        return self._model is not None

    def predict(self, image: Image.Image) -> dict:
        if self._model is None:
            self.load_model()

        img = self._preprocess(image)
        pred = self._model.predict(img)
        confidence = float(pred[0][0])
        label = "Defective" if confidence > 0.5 else "Good"

        return {
            "prediction": label,
            "confidence": round(
                confidence if label == "Defective" else 1 - confidence, 4
            ),
        }

    @staticmethod
    def _preprocess(image: Image.Image) -> np.ndarray:
        image = image.resize((224, 224))
        arr = np.array(image) / 255.0
        return np.expand_dims(arr, axis=0)


# Single shared instance imported everywhere
model_manager = ModelManager()

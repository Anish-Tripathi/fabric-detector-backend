import numpy as np
from PIL import Image
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)

try:
    import tflite_runtime.interpreter as tflite

    TFLITE_RUNTIME = True
except ImportError:
    import tensorflow as tf

    tflite = tf.lite
    TFLITE_RUNTIME = False


class ModelManager:
    """Singleton wrapper around the TFLite model."""

    def __init__(self):
        self._interpreter = None
        self._input_details = None
        self._output_details = None

    def load_model(self):
        if self._interpreter is None:
            model_path = settings.MODEL_PATH
            if model_path.endswith(".keras"):
                model_path = model_path.replace(".keras", ".tflite")

            logger.info(f"Loading TFLite model from: {model_path}")

            if TFLITE_RUNTIME:
                # tflite_runtime needs flex delegate for SELECT_TF_OPS
                try:
                    from tflite_runtime.interpreter import load_delegate

                    delegates = [load_delegate("libflexdelegate.so")]
                    self._interpreter = tflite.Interpreter(
                        model_path=model_path, experimental_delegates=delegates
                    )
                except Exception:
                    # Fall back without delegate
                    self._interpreter = tflite.Interpreter(model_path=model_path)
            else:
                self._interpreter = tflite.Interpreter(model_path=model_path)

            self._interpreter.allocate_tensors()
            self._input_details = self._interpreter.get_input_details()
            self._output_details = self._interpreter.get_output_details()
            logger.info("TFLite model ready.")

    def is_loaded(self) -> bool:
        return self._interpreter is not None

    def predict(self, image: Image.Image) -> dict:
        if self._interpreter is None:
            self.load_model()

        img = self._preprocess(image)
        self._interpreter.set_tensor(self._input_details[0]["index"], img)
        self._interpreter.invoke()
        pred = self._interpreter.get_tensor(self._output_details[0]["index"])

        if pred.shape[-1] == 2:
            good_prob = float(pred[0][0])
            defective_prob = float(pred[0][1])
            if defective_prob > good_prob:
                label = "Defective"
                confidence = defective_prob
            else:
                label = "Good"
                confidence = good_prob
        else:
            confidence_raw = float(pred[0][0])
            if confidence_raw > 0.5:
                label = "Defective"
                confidence = confidence_raw
            else:
                label = "Good"
                confidence = 1 - confidence_raw

        return {
            "prediction": label,
            "confidence": round(confidence, 4),
        }

    @staticmethod
    def _preprocess(image: Image.Image) -> np.ndarray:
        image = image.convert("RGB")
        image = image.resize((224, 224))
        arr = np.array(image, dtype=np.float32) / 255.0
        return np.expand_dims(arr, axis=0)


model_manager = ModelManager()

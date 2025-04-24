import cv2
import base64
import numpy as np
from io import BytesIO
from PIL.Image import Image

class ImageHandler:
    def __init__(self, image: Image | None = None):
        self.image = image

    def set_image(self, image: Image) -> None:
        self.image = image

    def convert_to_base64(self) -> str:
        if self.image is None:
            raise ValueError("No image provided")

        return ImageHandler.PIL_image_to_base64(self.image)
    
    @staticmethod
    def PIL_image_to_base64(pil_image: Image) -> str:
        buffer = BytesIO()
        pil_image.save(buffer, format="PNG")
        base64_str = base64.b64encode(buffer.getvalue()).decode("utf-8")
        return base64_str

    @staticmethod
    def PIL_to_gray_cv_image(pil_image: Image) -> cv2.Mat:
        cv_image_rgb = np.array(pil_image)
        cv_image_rgb = np.float32(cv_image_rgb)
        cv_image_gray = cv2.cvtColor(cv_image_rgb, cv2.COLOR_RGB2GRAY)
        return cv_image_gray
    
    @staticmethod
    def base64_to_gray_cv_image(base64_image: str) -> cv2.Mat:
        if base64_image.startswith("data:"):
            base64_image = base64_image.split("base64,")[1]
        decoded_image = base64.b64decode(base64_image)
        img_array = np.frombuffer(decoded_image, dtype=np.uint8)
        cv_image_gray = cv2.imdecode(img_array, cv2.IMREAD_GRAYSCALE)
        return cv_image_gray.astype(np.float32)
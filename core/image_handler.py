import cv2
import base64
import numpy as np
from io import BytesIO
from PIL.Image import Image, Resampling
from PIL.ImageEnhance import Contrast, Sharpness

class ImageHandler:
    @staticmethod
    def preprocess(image: Image, crop_fraction: float = 0.8) -> Image:
        img = image.convert("RGB")

        width, height = img.size
        new_width = int(width * crop_fraction)
        new_height = int(height * crop_fraction)

        left = (width - new_width) // 2
        top = (height - new_height) // 2

        img = img.crop((left, top, left + new_width, top + new_height))
        img = img.resize((512, 512), Resampling.LANCZOS)
        
        img = Contrast(img).enhance(1.1)
        img = Sharpness(img).enhance(1.3)

        return img

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